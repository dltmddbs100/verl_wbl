# 홈 설정
export HOME=/mnt/nlpai-storage/training_team/dltmddbs100
mkdir -p $HOME/.local
export PATH="$HOME/.local/bin:$PATH"
export HF_HOME=/mnt/nlpai-storage/training_team/dltmddbs100/.cache/huggingface


# cd /mnt/nlpai-storage/training_team/shared/verl_wbl
# pip install --no-deps -e .
# pip install math-verify

# # vllm server
# # 이미 별도 노드로 띄움
# vllm serve verl-team/GenRM-CI-Test-1.5B \
#   --served-model-name vllm \
#   --host 0.0.0.0 \
#   --port 11111

set -x

######################## 실행 설정값들 ########################
max_prompt_length=1024
max_response_length=2048


# Paths
MODEL_PATH="Qwen/Qwen3-8B" # Huggingface config 경로명
DIST_CKPT_PATH="/mnt/nlpai-storage/training_team/dltmddbs100/checkpoints/test/Qwen3-8B/" # 실제 dist ckpt 경로
# train_data_path=$HOME/data/LIMO/data.parquet
train_data_path=$HOME/data/gsm8k/train.parquet
# test_data_path="[$HOME/data/AIME_2024/data.parquet,$HOME/data/AIME_2025/data.parquet,$HOME/data/minerva/data.parquet]"
test_data_path=$HOME/data/AIME_2024/data.parquet


# Algorithm
temperature=1.0
top_p=1.0
top_k=-1 # 0 for HF rollout, -1 for vLLM rollout

val_temperature=0.6
val_top_p=0.95
val_top_k=20

ROLLOUT_MODE="sync"
N_ROLLS=2
TOTAL_STEPS=100

# Performance Related Parameter
use_dynamic_bsz=True
actor_ppo_max_token_len=$(((max_prompt_length + max_response_length)))
infer_ppo_max_token_len=$(((max_prompt_length + max_response_length)))
offload=True
optimizer_offload_fraction=1.0
USE_FUSED_KERNELS=False

ACTOR_PP=2
ACTOR_TP=4
ACTOR_VPP=null
ACTOR_CP=1
ACTOR_EP=1
ACTOR_ETP=1

INFER_TP=$ACTOR_PP

REF_PP=$ACTOR_PP
REF_VPP=$ACTOR_VPP
REF_CP=$ACTOR_CP
REF_TP=$ACTOR_TP
REF_EP=$ACTOR_EP
REF_ETP=$ACTOR_ETP

# Logging and Checkpointing
PROJECT_NAME="verl_multinode_genrm"
# EXP_NAME="GRPO_8b_mega_${ACTOR_TP}_${ACTOR_PP}_${ACTOR_EP}_N:${N_ROLLS}_step:${TOTAL_STEPS}_genrm"
EXP_NAME="GRPO_8b_mega_${ACTOR_TP}_${ACTOR_PP}_${ACTOR_EP}_N:${N_ROLLS}_test_genrm"
USE_DIST_CKPT=True


wandb login cea9842afe526a3d75e1e45f0153feee513f68fc


# 실행 코드
ray job submit \
    --address="http://train-ku-dltmddbs100-rl-worker-0.train-ku-dltmddbs100-rl-worker.p-ncai-wbl.svc.cluster.local:8265" \
    --runtime-env-json '{
        "working_dir": "/mnt/nlpai-storage/training_team/shared/verl",
        "env_vars": {
        "TOKENIZERS_PARALLELISM":"false",

        "GLOO_USE_IPV6": "0",
        "NCCL_SOCKET_IFNAME": "eth0",
        "GLOO_SOCKET_IFNAME": "eth0",
        "MASTER_ADDR": "198.18.20.139",
        "MASTER_PORT": "29500",

        "NCCL_NET_GDR_LEVEL": "2",
        "NCCL_IB_HCA": "mlx5_2,mlx5_3,mlx5_4,mlx5_5",
        "NCCL_IB_GID_INDEX": "0",
        "NCCL_NVLS_ENABLE": "1",
        "NCCL_CROSS_NIC": "0",
        "GLOO_SOCKET_FAMILY": "AF_INET",
        "TP_USE_IPV6": "0",
        "GLOO_USE_LIBUV": "0",
        "NCCL_DEBUG": "INFO",
        "NCCL_DEBUG_SUBSYS": "INIT,NET",
        "TORCH_NCCL_BLOCKING_WAIT": "1",
        "NCCL_ASYNC_ERROR_HANDLING": "1"
        }
    }' \
    -- \
    python3 -m verl.trainer.main_ppo --config-path=config \
        --config-name='ppo_megatron_trainer.yaml'\
        algorithm.adv_estimator=grpo \
        data.train_files=$train_data_path \
        data.val_files=$test_data_path \
        data.train_batch_size=256 \
        data.max_prompt_length=$max_prompt_length \
        data.max_response_length=$max_response_length \
        data.filter_overlong_prompts=True \
        data.truncation='error' \
        actor_rollout_ref.nccl_timeout=3000 \
        actor_rollout_ref.model.path=$MODEL_PATH \
        actor_rollout_ref.model.use_fused_kernels=$USE_FUSED_KERNELS \
        actor_rollout_ref.actor.optim.lr=1e-6 \
        actor_rollout_ref.actor.ppo_mini_batch_size=128 \
        actor_rollout_ref.actor.ppo_micro_batch_size_per_gpu=2 \
        actor_rollout_ref.actor.ppo_max_token_len_per_gpu=${actor_ppo_max_token_len} \
        actor_rollout_ref.actor.use_dynamic_bsz=True \
        actor_rollout_ref.actor.megatron.use_dist_checkpointing=${USE_DIST_CKPT} \
        actor_rollout_ref.actor.megatron.dist_checkpointing_path=${DIST_CKPT_PATH} \
        actor_rollout_ref.actor.megatron.param_offload=${offload} \
        actor_rollout_ref.actor.megatron.grad_offload=${offload} \
        actor_rollout_ref.actor.megatron.optimizer_offload=${offload} \
        actor_rollout_ref.actor.megatron.tensor_model_parallel_size=${ACTOR_TP} \
        actor_rollout_ref.actor.megatron.pipeline_model_parallel_size=${ACTOR_PP} \
        actor_rollout_ref.actor.megatron.virtual_pipeline_model_parallel_size=${ACTOR_VPP} \
        actor_rollout_ref.actor.megatron.context_parallel_size=${ACTOR_CP} \
        actor_rollout_ref.actor.checkpoint.async_save=True \
        actor_rollout_ref.rollout.log_prob_micro_batch_size_per_gpu=2 \
        actor_rollout_ref.rollout.log_prob_max_token_len_per_gpu=${infer_ppo_max_token_len} \
        actor_rollout_ref.rollout.name=vllm \
        actor_rollout_ref.rollout.mode=${ROLLOUT_MODE} \
        actor_rollout_ref.rollout.gpu_memory_utilization=0.8 \
        actor_rollout_ref.rollout.n=${N_ROLLS} \
        actor_rollout_ref.rollout.tensor_model_parallel_size=${INFER_TP} \
        actor_rollout_ref.rollout.max_num_batched_tokens=$((max_prompt_length + max_response_length)) \
        actor_rollout_ref.rollout.temperature=${temperature} \
        actor_rollout_ref.rollout.top_p=${top_p} \
        actor_rollout_ref.rollout.top_k=${top_k} \
        actor_rollout_ref.rollout.val_kwargs.temperature=${val_temperature} \
        actor_rollout_ref.rollout.val_kwargs.top_p=${val_top_p} \
        actor_rollout_ref.rollout.val_kwargs.top_k=${val_top_k} \
        actor_rollout_ref.rollout.val_kwargs.do_sample=True \
        actor_rollout_ref.rollout.val_kwargs.n=1 \
        actor_rollout_ref.rollout.enable_chunked_prefill=True \
        actor_rollout_ref.rollout.enforce_eager=True \
        actor_rollout_ref.rollout.free_cache_engine=True \
        actor_rollout_ref.rollout.dtype=bfloat16 \
        actor_rollout_ref.ref.megatron.dist_checkpointing_path=${DIST_CKPT_PATH} \
        actor_rollout_ref.ref.log_prob_micro_batch_size_per_gpu=2 \
        actor_rollout_ref.ref.log_prob_max_token_len_per_gpu=${infer_ppo_max_token_len} \
        actor_rollout_ref.ref.megatron.use_dist_checkpointing=${USE_DIST_CKPT} \
        actor_rollout_ref.ref.megatron.param_offload=${offload} \
        actor_rollout_ref.ref.megatron.tensor_model_parallel_size=${REF_TP} \
        actor_rollout_ref.ref.megatron.pipeline_model_parallel_size=${REF_PP} \
        actor_rollout_ref.ref.megatron.virtual_pipeline_model_parallel_size=${REF_VPP} \
        actor_rollout_ref.ref.megatron.context_parallel_size=${REF_CP} \
        +actor_rollout_ref.model.override_config.model_config.max_position_embeddings=$((max_prompt_length + max_response_length)) \
        +actor_rollout_ref.actor.optim.override_optimizer_config.optimizer_offload_fraction=${optimizer_offload_fraction} \
        +actor_rollout_ref.actor.optim.override_optimizer_config.overlap_cpu_optimizer_d2h_h2d=True \
        +actor_rollout_ref.actor.optim.override_optimizer_config.use_precision_aware_optimizer=True \
        +actor_rollout_ref.actor.optim.override_optimizer_config.optimizer_cpu_offload=True \
        +actor_rollout_ref.model.override_config.model_config.torch_dtype=float16 \
        reward_model.reward_manager=batch \
        custom_reward_function.path=/mnt/nlpai-storage/training_team/dltmddbs100/script/general_rl/reward_function.py \
        custom_reward_function.name=compute_score_batch \
        trainer.logger='["console","wandb"]' \
        trainer.project_name=$PROJECT_NAME \
        trainer.experiment_name=$EXP_NAME \
        trainer.n_gpus_per_node=8 \
        trainer.nnodes=$N_NODES \
        trainer.save_freq=20 \
        trainer.max_actor_ckpt_to_keep=1 \
        trainer.default_local_dir="/mnt/nlpai-storage/training_team/dltmddbs100/checkpoints/megatron/$PROJECT_NAME/$EXP_NAME" \
        trainer.val_before_train=True \
        trainer.test_freq=20 \
        trainer.total_epochs=3 \
        trainer.total_training_steps=$TOTAL_STEPS