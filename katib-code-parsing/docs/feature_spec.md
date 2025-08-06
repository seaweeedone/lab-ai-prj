# 상세 기능 정의서

## 1. 개요
머신러닝 코드를 관리하고, LLM을 이용하여 코드를 Katib에서 사용 가능한 형태로 파싱하는 시스템의 상세 기능 정의서이다.

---

## 2. 코드 관리

### 2.1. 기능 요구사항
- **코드 생성/수정/저장/삭제 (CRUD):** 사용자는 머신러닝 코드를 생성, 수정, 저장, 삭제할 수 있다.
- **코드 저장소:** 모든 머신러닝 코드는 `../ml-codes` 디렉토리에 Python 파일 형태로 저장된다.
- **목록 조회:**
    - 사용자는 코드 목록과 각 코드의 파싱 상태를 확인할 수 있는 페이지를 제공받는다.
    - 파싱 상태의 기본값은 'None'으로 표시된다.
    - 목록 조회 페이지에서 버튼 클릭을 통해 새 코드를 생성하고 저장할 수 있다.
- **상세 조회:**
    - 목록에서 특정 코드를 클릭하면 해당 코드의 상세 페이지로 이동한다.
    - 상세 페이지에는 버전별 코드와 함께 파싱 결과가 표시된다.
    - 파싱 결과 데이터가 없는 경우, 해당 영역은 비워둔다.
- **버전 관리:**
    - 코드는 버전별로 관리된다.
    - 코드 수정 후 저장 시, 새로운 버전으로 저장된다.
    - 상세 페이지에서 버전별 코드 조회가 가능하다.
    - 특정 버전의 코드를 삭제할 수 있다.
- **코드 수정:**
    - 상세 페이지 내 코드 영역을 클릭하면 코드 수정 모드로 전환된다.
    - '저장' 버튼 클릭 시, 새로운 버전으로 코드가 저장된다.
    - '취소' 버튼 클릭 시, 변경 사항은 폐기된다.

### 2.2. 데이터 모델
- **Code:**
    - `id`: (PK) 코드 고유 ID
    - `name`: 코드 이름
    - `created_at`: 생성 일시
    - `updated_at`: 수정 일시
- **CodeVersion:**
    - `id`: (PK) 버전 고유 ID
    - `code_id`: (FK) Code.id
    - `version`: 버전 번호 (e.g., 1, 2, 3...)
    - `content`: 코드 내용
    - `created_at`: 생성 일시

---

## 3. 코드 파싱

### 3.1. 기능 요구사항
- **LLM 기반 파싱:**
    - 코드 상세 페이지 내에서 'Parse' 버튼을 클릭하여 머신러닝 코드를 파싱하는 기능을 제공한다.
    - 파싱은 LLM을 사용하여, 주어진 머신러닝 코드를 논리적 블록으로 나누고 메타데이터를 추출하는 과정이다.
- **파싱 가이드 및 예시:**
    - 파싱 로직은 `examples/Code_Parsing_Guide.pdf` 파일의 가이드를 따른다.
    - `examples/org_code_iris.py` -> `examples/parsing_result_iris.json`
    - `examples/org_code_mnist.py` -> `examples/parsing_result_mnist.json`
- **파싱 입력 (LLM Prompt):**
    - LLM에 전달되는 프롬프트는 다음 구조를 가진다.
    ```
    You are a helpful assistant that parses machine learning code into logical blocks.

    **Instructions:**
    1.  Analyze the provided Python script.
    2.  Identify the machine learning framework used (e.g., "tensorflow", "pytorch", "scikit-learn").
    3.  Extract the names of the metrics used for evaluation (e.g., "accuracy", "loss").
    4.  Isolate the code block responsible for defining the model architecture ("model_block").
    5.  Isolate the code block responsible for command-line argument parsing where hyperparameters are defined ("parameter").
    6.  Isolate the code block responsible for loading data, preprocessing, training, and evaluation ("data_block").
    7.  Format the output as a single JSON object.

    **Python Code:**
    ```python
    {python_code_content}
    ```

    **JSON Output:**
    ```json
    ```
    - `{python_code_content}` 부분에 현재 화면에 표시된 버전의 코드가 삽입된다.
- **파싱 출력 (JSON):**
    - 파싱 결과는 다음 JSON 형식으로 생성된다.
    ```json
    {
      "name": "org_code_iris",
      "framework": "tensorflow",
      "metric": ["accuracy"],
      "parameter": "parser.add_argument('--batch-size', type=int, default=5,...)",
      "model_block": "import ...\n\ndef iris_model():\n    ...",
      "data_block": "def main():\n    parser = argparse.ArgumentParser()..."
    }
    ```
- **결과 저장 및 버전 관리:**
    - 파싱 결과(JSON)는 데이터베이스에 저장된다.
    - 파싱 결과는 코드 버전과 별개의 자체 버전을 가진다.
    - 하나의 코드 버전에 대해 여러 번의 파싱이 가능하다.
    - 파싱 결과의 이름은 자동으로 생성되지만(e.g., "Parsing Result v1"), 사용자가 수정할 수 있다.
    - 파싱 결과 또한 버전별 조회가 가능하다.
- **결과 수정 및 삭제:**
    - 파싱 결과가 표시된 영역(이름, JSON 데이터)을 클릭하면 수정 모드로 전환된다.
    - '저장' 버튼 클릭 시, 새로운 버전의 파싱 결과로 저장된다.
    - 특정 버전의 파싱 결과를 삭제할 수 있다.


### 3.2. 데이터 모델
- **ParsingResult:**
    - `id`: (PK) 파싱 결과 고유 ID
    - `code_version_id`: (FK) CodeVersion.id
    - `name`: 파싱 결과 이름
    - `created_at`: 생성 일시
- **ParsingResultVersion:**
    - `id`: (PK) 파싱 결과 버전 고유 ID
    - `parsing_result_id`: (FK) ParsingResult.id
    - `version`: 버전 번호
    - `content`: 파싱 결과 JSON 데이터
    - `created_at`: 생성 일시

---

## 4. 개발 규칙
개발 환경 및 코드 컨벤션 등은 `./dev-rules.md` 파일을 따른다.