# ruff: noqa: E501

import json

from openai import OpenAI

from app.common.constants import OPENAI_API_KEY

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


def get_llm_prompt(code_content: str) -> str:
    """
    Generates the prompt for the LLM based on the feature specification.
    """
    return f"""
You are a helpful assistant that parses machine learning code into logical blocks.

**Instructions:**
1. Analyze the provided Python script.
2. Identify the machine learning framework used (e.g., "tensorflow", "pytorch", "scikit-learn").
3. Extract the names of the metrics used for evaluation (e.g., "accuracy", "loss").
4. Isolate the code block responsible for defining the model architecture ("model_block").
5. Isolate the code block responsible for command-line argument parsing where hyperparameters are defined ("parameter").
6. Isolate the code block responsible for loading data, preprocessing, training, and evaluation ("data_block"). If there is a line in this code that runs the main function, add it to this block.
7. Format the output as a single JSON object without any additional explanations or markdown formatting.

**Python Code:**
```python
{code_content}
```

**JSON Output:**
```json
"""


async def parse_code_with_llm(code_content: str) -> dict:
    """
    Parses the given machine learning code using an LLM.

    Args:
        code_content: The string content of the python code.

    Returns:
        A dictionary containing the parsed code blocks and metadata.
    """
    prompt = get_llm_prompt(code_content)

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that parses machine learning code into logical blocks and outputs JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )

        response_content = response.choices[0].message.content
        if response_content is None:
            raise ValueError("LLM response content is empty")

        parsed_json = json.loads(response_content)

        # Ensure 'name' field exists, default to 'unnamed_code' if not present
        if "name" not in parsed_json:
            parsed_json["name"] = "unnamed_code"

        # Rename 'metrics' to 'metric' if 'metrics' exists
        if "metrics" in parsed_json:
            parsed_json["metric"] = parsed_json.pop("metrics")

        return parsed_json

    except Exception as e:
        print(f"An error occurred while parsing with LLM: {e}")
        raise
