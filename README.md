# Dose2Risk: A Computational Pipeline for Cancer Risk Estimation from Ionizing Radiation

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/release/python-380/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) 

**Leia este documento em outros idiomas:** [Português (BR)](LEIAME.md)

---

## Overview

Dose2Risk is a scientific software tool that processes radiation dose data from HotSpot simulations to estimate cancer risk associated with ionizing radiation exposure. It implements the epidemiological models from the **BEIR V** and **BEIR VII** reports.

The system is designed for applications in radiation protection, nuclear emergency response, and risk analysis in radionuclide-exposed areas, providing automated and transparent results for researchers and professionals.


[https://glofix-risk.qglaox.easypanel.host/](https://glofix-risk.qglaox.easypanel.host/)


![image](https://github.com/user-attachments/assets/020d4523-50f5-4350-8867-038631c768c8)
*Figure 1: The user-friendly web interface for uploading data and processing risks.*

## Features

- **Automated Data Extraction**: Seamlessly parses data from HotSpot output files.
- **Risk Calculation**: Computes cancer risk for various organs and scenarios using BEIR V and BEIR VII models.
- **Web Interface**: A modern, user-friendly web UI (built with Flask) for easy file uploads, parameter input, and result downloads.
- **Command-Line Interface**: A robust CLI for batch processing and integration into automated pipelines.
- **Customizable Parameters**: Allows users to specify age at exposure, age at assessment, and other relevant parameters.
- **Detailed Reporting**: Generates comprehensive CSV reports and detailed processing logs.
- **Internationalization (i18n)**: Supports multiple languages (English, Portuguese, Spanish, French).

## How to Cite

If you use this software in your research, please cite it as follows:

> [BARROS A.R., et.al], **Dose2Risk: A Computational Pipeline for Cancer Risk Estimation from Ionizing Radiation**, (2025), GitHub repository, [https://github.com/alvaroriz/dose2risk](https://github.com/alvaroriz/dose2risk)

*INSERIR REFERÊNCIA DO ARTIGO*

## Installation

To run this project, you need Python 3.8+ and the required libraries.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/alvaroriz/dose2risk.git
    cd dose2risk
    ```

2.  **Install dependencies:**
    It is recommended to use a virtual environment.
    ```bash
    # Create and activate a virtual environment (optional but recommended)
    python -m venv .venv
    source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`

    # Install the required packages
    pip install -r requirements.txt
    ```

## Usage

You can use Dose2Risk through its web interface or the command-line interface.

### Option 1: Web Interface (Recommended)

The web interface is the easiest way to use the tool.

1.  **Start the web server:**
    ```bash
    python app_web.py
    ```

2.  **Access the application:**
    Open your web browser and navigate to `http://127.0.0.1:5000`.

3.  **Follow the workflow:**
    -   Upload one or more HotSpot `.txt` files.
    -   Enter the required parameters (e.g., age at exposure, current age).
    -   Click "Process" to run the pipeline.
    -   Download the generated CSV and LOG files directly from the interface.

### Option 2: Command-Line Interface (CLI)

The CLI is ideal for batch processing or integration with other scripts.

1.  **Prepare your data:**
    -   Place your HotSpot input files (`.txt`) in a directory (e.g., `ExemploArquivoEntrada/`).
    -   Ensure the reference data files are in the `dados_referencia/` directory.

2.  **Run the pipeline:**
    ```bash
    python hotspot_to_risk.py --input_dir ExemploArquivoEntrada/ --output_dir saidas/ --exp_age 10 --att_age 30
    ```

3.  **Command-line arguments:**
    -   `--input_dir`: Path to the directory containing HotSpot files.
    -   `--output_dir`: Path to the directory where results will be saved.
    -   `--exp_age`: Age at exposure (in years).
    -   `--att_age`: Age at risk assessment (in years).

4.  **Check the results:**
    The output files (CSV and LOG) will be saved in the specified `output_dir`.

## Project Structure

```
Programa_Python_AR/
├── app_web.py             # Flask web application
├── hotspot_to_risk.py     # Main CLI processing script
├── requirements.txt       # Project dependencies
├── babel.cfg              # Configuration for i18n
├── translations/          # Language translation files
├── templates/             # HTML templates for the web app
├── static/                # Static files (CSS, JS, images)
├── dados_referencia/      # Reference data and parameters (e.g., BEIR tables)
├── ExemploArquivoEntrada/ # Example HotSpot input files
├── saidas/                # Default directory for output results
├── uploads/               # Directory for temporary file uploads
└── README.md              # This file
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Scientific References

-   **BEIR VII (2006):** Health Risks from Exposure to Low Levels of Ionizing Radiation (National Academy of Sciences).
-   **BEIR V (1990):** Health Effects of Exposure to Low Levels of Ionizing Radiation.

---

**Developed for applications in Radiation Protection, Nuclear Emergencies, and Scientific Research.**
