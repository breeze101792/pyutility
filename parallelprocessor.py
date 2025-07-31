import multiprocessing
import time

from concurrent.futures import ThreadPoolExecutor, as_completed

class ParallelProcessorManager:
    """
    A class to perform parallel processing of a list of items using multiprocessing.
    """

    def __init__(self, analyze_func, num_workers=4, process_chunk_by_chunk=False, debug_mode=False):
        """
        Initializes the ParallelProcessor.

        Args:
            analyze_func (callable): The function to apply to each item or a chunk of items.
            num_workers (int): The number of processes to use for parallelization.
            process_chunk_by_chunk (bool): If True, analyze_func will receive a list (chunk) of items.
                                           If False, analyze_func will receive items one by one.
            debug_mode (bool): If True, print debug messages during processing.
        """
        self.analyze_func = analyze_func
        self.num_workers = num_workers
        self.process_chunk_by_chunk = process_chunk_by_chunk
        self.debug_mode = debug_mode

    @staticmethod
    def _process_chunk(chunk, return_list, index, analyze_func, process_chunk_by_chunk, debug_mode):
        """
        Worker function for each process to analyze a chunk of items.

        Args:
            chunk (list): A sublist of items to process.
            return_list (multiprocessing.Manager.dict): A shared dictionary to store results.
            index (int): The index of the chunk, used as a key in return_list.
            analyze_func (callable): The function to apply to each item or a chunk of items.
            process_chunk_by_chunk (bool): If True, analyze_func will receive the entire chunk.
                                           If False, analyze_func will receive items one by one.
            debug_mode (bool): If True, print debug messages.
        """
        if debug_mode:
            print(f"Debug: Process {multiprocessing.current_process().name} starting chunk {index} (size: {len(chunk)})")

        try:
            if process_chunk_by_chunk:
                result = analyze_func(chunk)
            else:
                result = [analyze_func(item) for item in chunk]
            return_list[index] = result
        except Exception as e:
            if debug_mode:
                print(f"Debug: Error processing chunk {index} in process {multiprocessing.current_process().name}: {e}")
            return_list[index] = [] # Return empty list for the failed chunk

    def process(self, items):
        """
        Main parallel processing function.

        Args:
            items (list): The list of items to be processed.

        Returns:
            list: A list of processed results, merged in order.
        """
        if self.debug_mode:
            print(f"Debug: Starting parallel processing of {len(items)} items with {self.num_workers} processes.")
        if not items:
            if self.debug_mode:
                print("Debug: No items to process. Returning empty list.")
            return []

        chunk_size = (len(items) + self.num_workers - 1) // self.num_workers
        chunks = [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]

        manager = multiprocessing.Manager()
        results_dict = manager.dict()
        processes = []

        for idx, chunk in enumerate(chunks):
            if self.debug_mode:
                print(f"Debug: Starting process for chunk {idx} (size: {len(chunk)})")
            p = multiprocessing.Process(
                target=ParallelProcessor._process_chunk,
                args=(chunk, results_dict, idx, self.analyze_func, self.process_chunk_by_chunk, self.debug_mode)
            )
            p.start()
            processes.append(p)

        for p in processes:
            p.join()

        # Merge results in order
        merged_result = []
        for idx in range(len(chunks)):
            merged_result.extend(results_dict[idx])

        if self.debug_mode:
            print(f"Debug: Parallel processing finished. Merged results({len(results_dict.items())}).")
        return merged_result

# Queue
class ParallelProcessorQueue:
    def __init__(self, analyze_func, num_workers=4, process_chunk_by_chunk=False, debug_mode=False):
        self.analyze_func = analyze_func
        self.num_workers = num_workers
        self.process_chunk_by_chunk = process_chunk_by_chunk
        self.debug_mode = debug_mode

    def process(self, items):
        """Main parallel processing function."""
        if self.debug_mode:
            print(f"Debug: Starting parallel processing of {len(items)} items with {self.num_workers} processes.")

        if not items:
            if self.debug_mode:
                print("Debug: No items to process. Returning empty list.")
            return []

        chunk_size = (len(items) + self.num_workers - 1) // self.num_workers
        chunks = [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]

        queue = multiprocessing.Queue()
        processes = []

        for idx, chunk in enumerate(chunks):
            if self.debug_mode:
                print(f"Debug: Starting process for chunk {idx} (size: {len(chunk)})")

            p = multiprocessing.Process(
                target=ParallelProcessor._process_chunk,
                args=(chunk, queue, idx, self.analyze_func, self.process_chunk_by_chunk, self.debug_mode)
            )
            p.start()
            processes.append(p)

        # Collect results
        results_dict = {}
        if self.debug_mode:
            print(f"Debug: Collect process result.")
        for _ in range(len(chunks)):
            index, result = queue.get()
            results_dict[index] = result

        if self.debug_mode:
            print(f"Debug: Starting process join.")

        for p in processes:
            p.join()

        # Merge results by original chunk order
        merged_result = []
        for idx in range(len(chunks)):
            merged_result.extend(results_dict[idx])

        if self.debug_mode:
            print(f"Debug: Parallel processing finished. Merged results({len(results_dict.items())}).")
        return merged_result

    @staticmethod
    def _process_chunk(chunk, queue, index, analyze_func, process_chunk_by_chunk, debug_mode):
        """Worker function for each process to analyze a chunk of items."""
        if debug_mode:
            print(f"Debug: Process {multiprocessing.current_process().name} starting chunk {index} (size: {len(chunk)})")

        try:
            if process_chunk_by_chunk:
                result = analyze_func(chunk)
            else:
                result = [analyze_func(item) for item in chunk]
            queue.put((index, result))
        except Exception as e:
            if debug_mode:
                print(f"Debug: Error processing chunk {index} in process {multiprocessing.current_process().name}: {e}")
            queue.put((index, [])) # Return empty list for the failed chunk


# Threading.
class ParallelProcessorThread:
    def __init__(self, analyze_func, num_workers=4, process_chunk_by_chunk=False, debug_mode=False):
        self.analyze_func = analyze_func
        self.num_workers = num_workers
        self.process_chunk_by_chunk = process_chunk_by_chunk
        self.debug_mode = debug_mode

    def process(self, items):
        """Main parallel processing function."""
        if self.debug_mode:
            print(f"Debug: Starting parallel processing of {len(items)} items with {self.num_workers} threads.")

        if not items:
            if self.debug_mode:
                print("Debug: No items to process. Returning empty list.")
            return []

        # Split items into chunks
        chunk_size = (len(items) + self.num_workers - 1) // self.num_workers
        chunks = [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]

        results_dict = {}

        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            futures = {}
            for idx, chunk in enumerate(chunks):
                if self.debug_mode:
                    print(f"Debug: Submitting thread for chunk {idx} (size: {len(chunk)})")

                future = executor.submit(
                    self._process_chunk, chunk, idx, self.analyze_func, self.process_chunk_by_chunk, self.debug_mode
                )
                futures[future] = idx

            for future in as_completed(futures):
                idx, result = future.result()
                results_dict[idx] = result

        # Merge results in original order
        merged_result = []
        for idx in range(len(chunks)):
            merged_result.extend(results_dict[idx])

        if self.debug_mode:
            print(f"Debug: Parallel processing finished. Merged results({len(results_dict.items())}).")
        return merged_result

    @staticmethod
    def _process_chunk(chunk, index, analyze_func, process_chunk_by_chunk, debug_mode):
        """Worker function for each thread to analyze a chunk of items."""
        if debug_mode:
            print(f"Debug: Thread starting chunk {index} (size: {len(chunk)})")

        try:
            if process_chunk_by_chunk:
                result = analyze_func(chunk)
            else:
                result = [analyze_func(item) for item in chunk]
            return index, result
        except Exception as e:
            if debug_mode:
                print(f"Debug: Error processing chunk {index} in thread: {e}")
            return index, [] # Return empty list for the failed chunk


ParallelProcessor = ParallelProcessorQueue

# === Usage example ===
def analyze(item):
    # Simulate a heavy computation
    import random
    time.sleep(random.uniform(0.005, 0.015))
    # print(f"processed-{item} done") # This print is now controlled by the ParallelProcessor's debug_mode
    return f"processed-{item}"

def analyze_chunk(items_chunk):
    # Simulate a heavy computation for a chunk of items
    import random
    time.sleep(random.uniform(0.005, 0.015))
    # print(f"processed-chunk-{items_chunk[0]}-{items_chunk[-1]} done") # This print is now controlled by the ParallelProcessor's debug_mode
    return [f"processed-chunk-{item}" for item in items_chunk]

if __name__ == "__main__":
    item_list = list(range(100))  # Simulate your workload

    print("--- Processing items one by one (default mode, debug enabled) ---")
    # Create an instance of the ParallelProcessor for item-by-item processing with debug mode enabled
    processor_item_by_item = ParallelProcessor(analyze_func=analyze, num_workers=8, debug_mode=True)
    results_item_by_item = processor_item_by_item.process(item_list)

    print(f"Processed {len(results_item_by_item)} items.")
    print(results_item_by_item[:10], "...")

    print("\n--- Processing chunks (debug disabled) ---")
    # Create an instance of the ParallelProcessor for chunk processing with debug mode disabled
    processor_chunk = ParallelProcessor(analyze_func=analyze_chunk, num_workers=8, process_chunk_by_chunk=True, debug_mode=False)
    results_chunk = processor_chunk.process(item_list)

    print(f"Processed {len(results_chunk)} items.")
    print(results_chunk[:10], "...")

