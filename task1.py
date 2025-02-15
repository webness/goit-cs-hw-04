import os
import shutil
import threading
import multiprocessing
import re
from faker import Faker


def prepare_files():
    directory = './files'
    if os.path.exists(directory):
        shutil.rmtree(directory)
    os.makedirs(directory)

    fake = Faker()
    for i in range(100):
        filename = os.path.join(directory, f'file_{i + 1}.txt')
        with open(filename, 'w', encoding='utf-8') as f:
            # Записуємо 5 випадкових речень у кожен файл
            sentences = [fake.sentence() for _ in range(5)]
            f.write(' '.join(sentences))


def extract_keywords_from_files(num_keywords=4, num_files=3, words_per_file=2):
    directory = './files'
    files = sorted([os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.txt')])
    keywords = []
    for file in files[:num_files]:
        with open(file, 'r', encoding='utf-8') as f:
            text = f.read()
        words = re.findall(r'\b\w+\b', text)
        keywords.extend(words[:words_per_file])
        if len(keywords) >= num_keywords:
            break
    unique_keywords = []
    for word in keywords:
        if word not in unique_keywords:
            unique_keywords.append(word)
        if len(unique_keywords) == num_keywords:
            break
    return unique_keywords


def search_in_files_thread(file_list, keywords, results):
    for file in file_list:
        with open(file, 'r', encoding='utf-8') as f:
            text = f.read()
        found_keywords = {}
        for keyword in keywords:
            count = text.lower().count(keyword.lower())
            if count > 0:
                found_keywords[keyword] = count
        if found_keywords:
            results.append((file, found_keywords))


def threading_search(keywords):
    directory = './files'
    files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.txt')]
    num_threads = 4
    threads = []
    results = []
    chunk_size = len(files) // num_threads

    for i in range(num_threads):
        start = i * chunk_size
        end = len(files) if i == num_threads - 1 else (i + 1) * chunk_size
        thread_files = files[start:end]
        t = threading.Thread(target=search_in_files_thread, args=(thread_files, keywords, results))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print("Результати пошуку (threading) для ключових слів", keywords, ":")
    for res in results:
        print(res)


def search_in_files_process(file_list, keywords, result_queue):
    for file in file_list:
        with open(file, 'r', encoding='utf-8') as f:
            text = f.read()
        found_keywords = {}
        for keyword in keywords:
            count = text.lower().count(keyword.lower())
            if count > 0:
                found_keywords[keyword] = count
        if found_keywords:
            result_queue.put((file, found_keywords))


def multiprocessing_search(keywords):
    directory = './files'
    files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.txt')]
    num_processes = 4
    processes = []
    result_queue = multiprocessing.Queue()
    chunk_size = len(files) // num_processes

    for i in range(num_processes):
        start = i * chunk_size
        end = len(files) if i == num_processes - 1 else (i + 1) * chunk_size
        proc_files = files[start:end]
        p = multiprocessing.Process(target=search_in_files_process, args=(proc_files, keywords, result_queue))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    results = []
    while not result_queue.empty():
        results.append(result_queue.get())

    print("Результати пошуку (multiprocessing) для ключових слів", keywords, ":")
    for res in results:
        print(res)


if __name__ == '__main__':
    prepare_files()
    print("Файли підготовлено.")

    KEYWORDS = extract_keywords_from_files()
    print("Вибрані ключові слова:", KEYWORDS)
    print("=" * 5)

    threading_search(KEYWORDS)
    print("=" * 5)

    multiprocessing_search(KEYWORDS)
