#!/bin/bash

echo "🔍 vLLM 서버 연결 테스트"
echo "========================"

# vllm 서버 주소
VLLM_URL="http://vllm-genrm-server-0.vllm-genrm-server.p-ncai-wbl.svc.cluster.local:11111"

# 1. DNS 해석 테스트
echo "1. DNS 해석 테스트..."
if getent hosts vllm-genrm-server-0.vllm-genrm-server.p-ncai-wbl.svc.cluster.local; then
    echo "✓ DNS 해석 성공"
else
    echo "✗ DNS 해석 실패"
    exit 1
fi

# 2. 포트 연결 테스트
echo ""
echo "2. 포트 연결 테스트..."
if timeout 5 bash -c "cat < /dev/null > /dev/tcp/vllm-genrm-server-0.vllm-genrm-server.p-ncai-wbl.svc.cluster.local/11111"; then
    echo "✓ 포트 11111 연결 가능"
else
    echo "✗ 포트 11111 연결 불가"
    exit 1
fi

# 3. HTTP 엔드포인트 테스트
echo ""
echo "3. HTTP 엔드포인트 테스트..."
if curl -s -f "$VLLM_URL/v1/models" > /dev/null; then
    echo "✓ HTTP 요청 성공"
    echo "사용 가능한 모델:"
    curl -s "$VLLM_URL/v1/models" | python3 -m json.tool
else
    echo "✗ HTTP 요청 실패"
    exit 1
fi

# 4. Chat Completion 테스트
echo ""
echo "4. Chat Completion API 테스트..."
RESPONSE=$(curl -s -X POST "$VLLM_URL/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -d '{
        "model": "vllm",
        "messages": [{"role": "user", "content": "What is 2+2?"}],
        "max_tokens": 1024
    }')

if echo "$RESPONSE" | grep -q "choices"; then
    echo "✓ Chat API 요청 성공"
    echo "응답:"
    echo "$RESPONSE" | python3 -m json.tool
else
    echo "✗ Chat API 요청 실패"
    echo "$RESPONSE"
    exit 1
fi

echo ""
echo "✅ 모든 테스트 통과!"