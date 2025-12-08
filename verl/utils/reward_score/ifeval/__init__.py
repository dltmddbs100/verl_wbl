import json
import logging
import requests
from time import sleep

from .utils import compute_rule_score

logger = logging.getLogger(__name__)

BASE_URL = ""
API_KEY = ""
MAX_RETRIES = 3
BASE_DELAY = 2
MODEL_NAME = ""

def get_response(prompt):
    messages = [{"role": "user", "content": prompt}]
    for attempt in range(MAX_RETRIES):
        try:
            headers = {"Content-Type": "application/json"}
            if API_KEY != "": headers["Authorization"] = f"Bearer {API_KEY}"
            chat_url = f"{BASE_URL}/v1/chat/completions"
            data = {"model": MODEL_NAME, "messages": messages}
            output = requests.post(chat_url, headers=headers, json=data, timeout=30)
            response = output.json()["choices"][0]["message"]["content"]
            return response
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                print("Exception: ", repr(e))
                delay = BASE_DELAY * (2**attempt)
                print(f"Retrying in {delay} seconds...")
                sleep(delay)
            else:
                print(f"Failed after {MAX_RETRIES} attempts. Error: {e}")

    raise ConnectionRefusedError(f"Failed to run the model for {prompt}!")

def compute_reward(response):
    reward_score = 0.0
    try:
        if '[Evaluation Score]:' in response:
            response = response.split('[Evaluation Score]:')[-1].strip()[0]
            reward_score = float(response) / 3
    except: 
        pass
    return reward_score

def compute_score(solution, ground_truth, extra_info):
    solution = solution.split("</think>")[-1].strip()

    if not isinstance(ground_truth, dict):
        ground_truth = json.loads(ground_truth)

    genrm_prompt = extra_info["genrm_prompt"]

    rule_score_list = compute_rule_score(solution, ground_truth)
    rule_score = sum(rule_score_list) / len(rule_score_list)

    problem = ground_truth['prompt']
    ground_truth.pop('prompt')
    prompt = genrm_prompt.format(problem=problem, solution=solution, ground_truth=str(ground_truth))
    response = get_response(prompt)

    if response is not None:
        response_score = compute_reward(response)
    else:
        response_score = 0.0

    a = 0.7
    reward_score = a * rule_score + (1-a) * response_score
    return reward_score
