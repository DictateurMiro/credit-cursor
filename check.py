import os
import sys
import json
import sqlite3
import platform
from colorama import Fore, Style, init
import logging
import re

init()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

EMOJI = {
    "USER": "👤",
    "FAST": "⭐",
    "SLOW": "📝",
    "ERROR": "❌",
    "WARNING": "⚠️"
}

def get_user_documents_path():
    if platform.system() == "Windows":
        return os.path.expanduser("~\\Documents")
    else:
        return os.path.expanduser("~/Documents")

def get_config():
    try:
        docs_path = get_user_documents_path()
        if not docs_path or not os.path.exists(docs_path):
            docs_path = os.path.abspath('.')
        config_dir = os.path.normpath(os.path.join(docs_path, ".cursor-free-vip"))
        config_file = os.path.normpath(os.path.join(config_dir, "config.ini"))
        import configparser
        config = configparser.ConfigParser()
        if os.path.exists(config_file):
            config.read(config_file, encoding='utf-8')
        return config
    except Exception:
        return None

def get_token_from_config():
    try:
        config = get_config()
        if not config:
            return None
        system = platform.system()
        if system == "Windows" and config.has_section('WindowsPaths'):
            return {
                'storage_path': config.get('WindowsPaths', 'storage_path'),
                'sqlite_path': config.get('WindowsPaths', 'sqlite_path'),
            }
        elif system == "Darwin" and config.has_section('MacPaths'):
            return {
                'storage_path': config.get('MacPaths', 'storage_path'),
                'sqlite_path': config.get('MacPaths', 'sqlite_path'),
            }
        elif system == "Linux" and config.has_section('LinuxPaths'):
            return {
                'storage_path': config.get('LinuxPaths', 'storage_path'),
                'sqlite_path': config.get('LinuxPaths', 'sqlite_path'),
            }
    except Exception as e:
        logger.error(f"Get config path failed: {str(e)}")
    return None

def get_token_from_storage(storage_path):
    if not os.path.exists(storage_path):
        return None
    try:
        with open(storage_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if 'cursorAuth/accessToken' in data:
                return data['cursorAuth/accessToken']
            for key in data:
                if 'token' in key.lower() and isinstance(data[key], str) and len(data[key]) > 20:
                    return data[key]
    except Exception as e:
        logger.error(f"get token from storage.json failed: {str(e)}")
    return None

def get_token_from_sqlite(sqlite_path):
    if not os.path.exists(sqlite_path):
        return None
    try:
        conn = sqlite3.connect(sqlite_path)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM ItemTable WHERE key LIKE '%token%'")
        rows = cursor.fetchall()
        conn.close()
        for row in rows:
            try:
                value = row[0]
                if isinstance(value, str) and len(value) > 20:
                    return value
                data = json.loads(value)
                if isinstance(data, dict) and 'token' in data:
                    return data['token']
            except:
                continue
    except Exception as e:
        logger.error(f"get token from sqlite failed: {str(e)}")
    return None

def get_token():
    paths = get_token_from_config()
    if not paths:
        return None
    token = get_token_from_storage(paths['storage_path'])
    if token:
        return token
    token = get_token_from_sqlite(paths['sqlite_path'])
    if token:
        return token
    return None

def get_email_from_storage(storage_path):
    if not os.path.exists(storage_path):
        return None
    try:
        with open(storage_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if 'cursorAuth/cachedEmail' in data:
                return data['cursorAuth/cachedEmail']
            for key in data:
                if 'email' in key.lower() and isinstance(data[key], str) and '@' in data[key]:
                    return data[key]
    except Exception as e:
        logger.error(f"get email from storage.json failed: {str(e)}")
    return None

def get_email_from_sqlite(sqlite_path):
    if not os.path.exists(sqlite_path):
        return None
    try:
        conn = sqlite3.connect(sqlite_path)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM ItemTable WHERE key LIKE '%email%' OR key LIKE '%cursorAuth%'")
        rows = cursor.fetchall()
        conn.close()
        for row in rows:
            try:
                value = row[0]
                if isinstance(value, str) and '@' in value:
                    return value
                try:
                    data = json.loads(value)
                    if isinstance(data, dict):
                        if 'email' in data:
                            return data['email']
                        if 'cachedEmail' in data:
                            return data['cachedEmail']
                except:
                    pass
            except:
                continue
    except Exception as e:
        logger.error(f"get email from sqlite failed: {str(e)}")
    return None

class UsageManager:
    @staticmethod
    def get_usage(token):
        import requests
        url = "https://www.cursor.com/api/usage"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Cookie": f"WorkosCursorSessionToken=user_01OOOOOOOOOOOOOOOOOOOOOOOO%3A%3A{token}"
        }
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            gpt4_data = data.get("gpt-4", {})
            premium_usage = gpt4_data.get("numRequestsTotal", 0)
            max_premium_usage = gpt4_data.get("maxRequestUsage", 999)
            gpt35_data = data.get("gpt-3.5-turbo", {})
            basic_usage = gpt35_data.get("numRequestsTotal", 0)
            return {
                'premium_usage': premium_usage,
                'max_premium_usage': max_premium_usage,
                'basic_usage': basic_usage,
                'max_basic_usage': "No Limit"
            }
        except Exception as e:
            logger.error(f"Get usage info failed: {str(e)}")
            return None

def display_account_info():
    token = get_token()
    if not token:
        print(f"{Fore.RED}{EMOJI['ERROR']} Token not found. Please login to Cursor first.{Style.RESET_ALL}")
        return
    paths = get_token_from_config()
    if not paths:
        print(f"{Fore.RED}{EMOJI['ERROR']} Configuration not found.{Style.RESET_ALL}")
        return
    email = get_email_from_storage(paths['storage_path'])
    if not email:
        email = get_email_from_sqlite(paths['sqlite_path'])
    if email:
        print(f"{Fore.GREEN}{EMOJI['USER']} Email: {Fore.WHITE}{email}{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}{EMOJI['WARNING']} Email not found{Style.RESET_ALL}")
    usage_info = UsageManager.get_usage(token)
    if usage_info:
        premium_usage = usage_info.get('premium_usage', 0)
        max_premium_usage = usage_info.get('max_premium_usage', "No Limit")
        if isinstance(max_premium_usage, str) and max_premium_usage == "No Limit":
            premium_color = Fore.YELLOW
            premium_display = f"{premium_usage}/{max_premium_usage}"
        else:
            if max_premium_usage is None or max_premium_usage == 0:
                max_premium_usage = 999
                premium_percentage = 0
            else:
                premium_percentage = (premium_usage / max_premium_usage) * 100
            premium_color = Fore.YELLOW
            premium_display = f"{premium_usage}/{max_premium_usage} ({premium_percentage:.1f}%)"
        print(f"{premium_color}{EMOJI['FAST']} Fast: {Fore.WHITE}{premium_display}{Style.RESET_ALL}")
        basic_usage = usage_info.get('basic_usage', 0)
        max_basic_usage = usage_info.get('max_basic_usage', "No Limit")
        if isinstance(max_basic_usage, str) and max_basic_usage == "No Limit":
            basic_color = Fore.BLUE
            basic_display = f"{basic_usage}/{max_basic_usage}"
        else:
            if max_basic_usage is None or max_basic_usage == 0:
                max_basic_usage = 999
                basic_percentage = 0
            else:
                basic_percentage = (basic_usage / max_basic_usage) * 100
            basic_color = Fore.BLUE
            basic_display = f"{basic_usage}/{max_basic_usage} ({basic_percentage:.1f}%)"
        print(f"{basic_color}{EMOJI['SLOW']} Slow: {Fore.WHITE}{basic_display}{Style.RESET_ALL}")

def main():
    try:
        display_account_info()
    except Exception as e:
        print(f"{Fore.RED}{EMOJI['ERROR']} Error: {str(e)}{Style.RESET_ALL}")

if __name__ == "__main__":
    main() 
