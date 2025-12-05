"""
GenRM 서버 테스트 스크립트
vllm 서버가 실행 중인지 확인하고 get_response 함수를 테스트합니다.
"""

from reward_function import get_response, compute_reward

def test_simple_math_problem():
    """간단한 수학 문제로 GenRM 서버 테스트"""
    
    # 테스트 케이스 1: 올바른 답변
    print("=" * 80)
    print("테스트 1: 올바른 수학 문제 풀이")
    print("=" * 80)
    
    problem = "What is 2 + 2?"
    solution = "2 + 2 = 4"
    ground_truth = "4"
    
    print(f"문제: {problem}")
    print(f"풀이: {solution}")
    print(f"정답: {ground_truth}")
    print()
    
    try:
        response = get_response(problem, solution, ground_truth)
        print(f"GenRM 응답:\n{response}\n")
        
        reward = compute_reward(response)
        print(f"보상 점수: {reward}")
        print()
    except Exception as e:
        print(f"오류 발생: {e}\n")
    
    # 테스트 케이스 2: 잘못된 답변
    print("=" * 80)
    print("테스트 2: 잘못된 수학 문제 풀이")
    print("=" * 80)
    
    problem = "What is 5 × 3?"
    solution = "5 × 3 = 12"  # 잘못된 답
    ground_truth = "15"
    
    print(f"문제: {problem}")
    print(f"풀이: {solution}")
    print(f"정답: {ground_truth}")
    print()
    
    try:
        response = get_response(problem, solution, ground_truth)
        print(f"GenRM 응답:\n{response}\n")
        
        reward = compute_reward(response)
        print(f"보상 점수: {reward}")
        print()
    except Exception as e:
        print(f"오류 발생: {e}\n")
    
    # 테스트 케이스 3: 복잡한 문제
    print("=" * 80)
    print("테스트 3: 복잡한 수학 문제")
    print("=" * 80)
    
    problem = "Solve for x: 3x + 7 = 22"
    solution = """
    3x + 7 = 22
    3x = 22 - 7
    3x = 15
    x = 5
    """
    ground_truth = "5"
    
    print(f"문제: {problem}")
    print(f"풀이: {solution}")
    print(f"정답: {ground_truth}")
    print()
    
    try:
        response = get_response(problem, solution, ground_truth)
        print(f"GenRM 응답:\n{response}\n")
        
        reward = compute_reward(response)
        print(f"보상 점수: {reward}")
        print()
    except Exception as e:
        print(f"오류 발생: {e}\n")



if __name__ == "__main__":
    print("\n🚀 GenRM 서버 테스트 시작\n")
    
    # 먼저 서버 연결 테스트
    test_simple_math_problem()
    
    
    print("\n✅ 테스트 완료\n")