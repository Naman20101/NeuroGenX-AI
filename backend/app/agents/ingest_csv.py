import pandas as pd
import os

class IngestCSV:
    """
    Agent responsible for ingesting a CSV file into a pandas DataFrame.
    It expects the dataset_id to be provided in the run context.
    """
    def run(self, ctx: dict):
        """
        Executes the ingestion step.

        Args:
            ctx (dict): The shared context dictionary for the run.
                        Must contain 'dataset_id'.

        Returns:
            dict: The updated context with the 'df' key containing
                  the pandas DataFrame.
        """
        dataset_id = ctx.get("dataset_id")
        if not dataset_id:
            print("--- ERROR: 'dataset_id' is missing from the context. Cannot ingest. ---")
            raise ValueError("'dataset_id' is missing from the run payload.")

        # This assumes your CSV files are in a 'data' folder
        # Adjust the path if your project structure is different
        file_path = os.path.join(os.getcwd(), 'data', dataset_id)

        print(f"--- IngestCSV Agent: Attempting to read file from path: {file_path} ---")

        try:
            # Read the CSV file into a pandas DataFrame
            df = pd.read_csv(file_path)
            ctx["df"] = df
            print(f"--- IngestCSV Agent: Successfully read {dataset_id} with {len(df)} rows. ---")

        except FileNotFoundError:
            # This error is the most likely cause of your 500 error
            print(f"--- ERROR: The file '{dataset_id}' was not found at '{file_path}'. ---")
            print("--- Please ensure the file is deployed in the correct location on Render. ---")
            raise  # Re-raise the error to stop the process

        except Exception as e:
            # Catch any other unexpected errors
            print(f"--- ERROR: An unexpected error occurred while reading the file: {e} ---")
            raise  # Re-raise the error

        return ctx

