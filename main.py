import os
import nltk
import logging
import multiprocessing
import threading
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed

from dotenv import load_dotenv
from google.cloud import storage
from generator import GenerateCorpus, Platform
from database import DatabaseManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BATCH_SIZE = 100


def log_process_thread_info(message):
    process_id = multiprocessing.current_process().pid
    thread_id = threading.current_thread().ident

    logger.info(
        f"{message} (Process ID: {process_id}, Thread ID: {thread_id})"
    )


def download_file(bucket_name, source_blob_name, destination_file_name):
    logger.info(
        f"Downloading {source_blob_name} to {destination_file_name}"
    )

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

    logger.info(
        f"Downloaded {source_blob_name} to {destination_file_name}"
    )


def process_batch(batch, dir_name, subreddit_id, file, batch_number, total_batches):
    log_process_thread_info(
        f"Processing batch {batch_number} out of {total_batches} for file {file}"
    )

    corpus_list = []
    for line in batch:
        line = line.strip()
        corpus_generator = GenerateCorpus(Platform.WIKI, dir_name, subreddit_id, "", line)
        corpus = corpus_generator.generate_corpus()
        if corpus is not None:
            corpus_list.append(corpus)

            logger.info(
                f"Batch {batch_number} out of {total_batches} for file {file} : {line}"
            )

    return corpus_list


def process_file(bucket_name, source_blob_name, raw_data_dir, dir_name):
    local_file_path = os.path.join(raw_data_dir, source_blob_name.split("/")[-1])
    download_file(bucket_name, source_blob_name, local_file_path)

    log_process_thread_info(
        f"Processing file {local_file_path}"
    )

    subreddit_id = int(local_file_path.split("_")[1][:2])
    with open(local_file_path, "r") as f:
        lines = f.readlines()
        batches = [lines[i:i + BATCH_SIZE] for i in range(0, len(lines), BATCH_SIZE)]
        total_batches = len(batches)
        database_manager = DatabaseManager()

        with ThreadPoolExecutor() as executor:

            future_to_batch = {
                executor.submit(process_batch, batch, dir_name, subreddit_id,
                                local_file_path, batch_num + 1, total_batches): batch
                for batch_num, batch in enumerate(batches)
            }

            for future in as_completed(future_to_batch):
                batch = future_to_batch[future]
                batch_number = batches.index(batch) + 1
                try:
                    batch_corpus_list = future.result()
                    if batch_corpus_list:

                        logger.info(
                            f"Inserting {len(batch_corpus_list)} corpuses into the database from batch "
                            f"{batch_number} of file {local_file_path}"
                        )

                        try_count = 10
                        while try_count > 0:
                            try:
                                database_manager.insert_corpuses(batch_corpus_list)
                                break
                            except Exception as exc:
                                logger.error(
                                    f"Batch {batch_number} out of {total_batches} for file "
                                    f"{local_file_path} generated an exception: {exc}"

                                )
                                database_manager.close_connection()
                                database_manager.create_connection()
                                try_count -= 1

                except Exception as exc:
                    logger.error(
                        f"Batch {batch_number} out of {total_batches} for file "
                        f"{local_file_path} generated an exception: {exc}"
                    )

    logger.info(
        f"Processed {len(lines)} lines from {local_file_path}"
    )

    os.remove(local_file_path)


def prepare():
    logger.info("Starting NLTK downloads")
    nltk.download("punkt")
    nltk.download("averaged_perceptron_tagger")
    nltk.download("maxent_ne_chunker")
    nltk.download("words")
    nltk.download("stopwords")
    nltk.download("wordnet")
    nltk.download("vader_lexicon")
    nltk.download("omw")
    nltk.download("universal_tagset")

    logger.info("NLTK downloads finished")


def inserter():
    load_dotenv()
    prepare()
    bucket_name = "cmpe492-wiki"
    raw_data_dir = "/tmp/data"
    os.makedirs(raw_data_dir, exist_ok=True)
    folders = ["1of2", "2of2"]

    chosen = os.getenv("INS_FOLDER")
    files = os.getenv("INS_FILES").split(",")

    with ProcessPoolExecutor() as executor:
        for folder in folders:
            if folder != chosen:
                continue

            blobs = storage.Client().list_blobs(bucket_name, prefix=folder + "/")
            # the files are just two digits, so we can filter them
            blobs = [blob for blob in blobs if blob.name.split("_")[-1] in files]

            future_to_blob = {
                executor.submit(process_file, bucket_name,
                                blob.name, raw_data_dir, folder): blob
                for blob in blobs
            }

            for future in as_completed(future_to_blob):
                blob = future_to_blob[future]
                try:
                    future.result()
                except Exception as exc:
                    logger.error(
                        f"{blob.name} generated an exception: {exc}"
                    )


if __name__ == "__main__":
    multiprocessing.set_start_method("spawn")
    inserter()
