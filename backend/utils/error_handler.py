import logging
import traceback

# Конфигурация логирования
logging.basicConfig(
    filename='error.log',
    level=logging.INFO,  # Уровень INFO, чтобы логировать не только ошибки
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def log_error(error: Exception, context: str = ""):
    """Логирование ошибки в файл."""
    error_message = f"{type(error).__name__}: {error}"
    full_message = f"[ERROR] {context} - {error_message}" if context else error_message
    logging.error(full_message)
    logging.error(traceback.format_exc())  # Полный стек ошибки
    return error_message  # Можно возвращать для API

def log_info(message: str):
    """Логирование информационных сообщений."""
    logging.info(f"[INFO] {message}")
