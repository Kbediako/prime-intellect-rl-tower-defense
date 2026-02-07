
# Config Reference - Hosted Training

Run RL training jobs using TOML config files with the `prime rl run` command.

## Quick Start

```bash
# Create a config file (defaults to rl.toml)
prime rl init

# Start a training run
prime rl run my-config.toml

# List runs
prime rl list

# View logs
prime rl logs <run-id>

# Follow logs in real-time
prime rl logs <run-id> --follow

# Stop a run
prime rl stop <run-id>

# Delete a run
prime rl delete <run-id>

```

## **Config File Examples**

### **Basic Config**

All RL training configs should specify:

-   `model`: which model to train
-   `max_steps`: number of steps to train (each step = 1 batch)
-   `batch_size`: number of _total rollouts_ per batch
-   `rollouts_per_example`: number of rollouts per example (within a batch)
    -   equivalent to the “group size”
    -   `batch_size` / `rollouts_per_example` should be an integer (groups per batch)
-   `[sampling].max_tokens`: number of tokens to sample from the model _per turn_
    -   technically optional, but should always be set to avoid non-terminating completions (which is more often an issue during RL training than evaluations of trained models)
    -   use to control sequence length (in conjuction with `max_turns` for some environments)
-   `[[env]].id`: which environment from the Environments Hub to train on
    -   `[[...]]` denotes a list in TOML files — multiple envs can be passed if desired

Example of a minimal config for: [https://app.primeintellect.ai/dashboard/environments/primeintellect/reverse-text](https://app.primeintellect.ai/dashboard/environments/primeintellect/reverse-text)

```toml
model = "PrimeIntellect/Qwen3-0.6B-Reverse-Text-SFT"
max_steps = 100
batch_size = 128
rollouts_per_example = 8

[sampling]
max_tokens = 2048

[[env]]
id = "your-username/your-env"


```

### **Configuring Environment Args**

Environments can expose

```toml
model = "PrimeIntellect/Qwen3-0.6B-Reverse-Text-SFT"
max_steps = 200
batch_size = 512
rollouts_per_example = 16
env_file = ["secrets.env", "api-keys.env"]  # Loaded relative to config file

[sampling]
max_tokens = 256
temperature = 1.0

[[env]]
id = "your-username/your-env"
name = "custom-args-run"
args = { dataset_split = "train", system_prompt = "You are a helpful assistant.", api_key_var = "CUSTOM_API_KEY"}


```

Environment args should _not_ be used to pass API credentials directly — instead, pass the _name_ of the variable, ensure that the credentials are passed via a `.env` file (or via CLI directly — run `prime rl run -h` for details), and use `os.getenv` in your environment code to load the variable.

### **Multi-Environment Training**

```toml
model = "PrimeIntellect/Qwen3-0.6B-Reverse-Text-SFT"
max_steps = 100
batch_size = 128
rollouts_per_example = 8

[sampling]
max_tokens = 2048

[[env]]
id = "primeintellect/alphabet-sort"

[[env]]
id = "primeintellect/reverse-text"


```

### **Config with Evaluation**

```toml
model = "PrimeIntellect/Qwen3-0.6B-Reverse-Text-SFT"
max_steps = 500
batch_size = 8
rollouts_per_example = 2

[sampling]
max_tokens = 128
temperature = 0.8

[[env]]
id = "your-username/your-env"

[eval]
interval = 100
num_examples = -1          # default for all eval environments (-1 = all)
rollouts_per_example = 1   # default for all eval environments
eval_base_model = true     # also evaluate the base model

[[eval.env]]
id = "your-username/eval-env"
args = { split = "test" }
num_examples = 30          # environment-specific override
rollouts_per_example = 4   # environment-specific override


```

### **Config with Validation**

Uses the `eval_dataset` from your training environment(s) to run periodic validation. Falls back to primary dataset if `eval_dataset` is not set.

Useful as a holdout sanity check, or for measuring reward curves if online difficulty filtering is enabled (which

```toml
model = "PrimeIntellect/Qwen3-0.6B-Reverse-Text-SFT"
max_steps = 500
batch_size = 128
rollouts_per_example = 8

[sampling]
max_tokens = 2048

[[env]]
id = "your-username/your-env"

[val]
num_examples = 64
rollouts_per_example = 1
interval = 5  # Run validation every 5 steps


```

### **Config with Buffer (Difficulty Filtering)**

```toml
model = "PrimeIntellect/Qwen3-0.6B-Reverse-Text-SFT"
max_steps = 500
batch_size = 128
rollouts_per_example = 8

[sampling]
max_tokens = 2048

[[env]]
id = "your-username/your-env"

[buffer]
online_difficulty_filtering = true
easy_threshold = 0.8
hard_threshold = 0.2
easy_fraction = 0.0
hard_fraction = 0.0
env_ratios = [0.5, 0.5]  # For multi-env training
skip_verification = false
seed = 42


```

### **Config with W&B Logging**

```toml
model = "PrimeIntellect/Qwen3-0.6B-Reverse-Text-SFT"
max_steps = 100
batch_size = 8
rollouts_per_example = 2

[sampling]
max_tokens = 128
temperature = 0.8

[[env]]
id = "your-username/your-env"

[wandb]
project = "my-rl-project"
entity = "my-team"
name = "experiment-1"


```

Then run with your W&B API key:

```bash
# If WANDB_API_KEY is already set in environment
prime rl run config.toml -e WANDB_API_KEY

# Or pass it directly
prime rl run config.toml -e WANDB_API_KEY=your-key

# Or use an env file
prime rl run config.toml --env-file secrets.env


```

### **Config with Env Files**

You can specify secret/environment files directly in the config:

```toml
model = "PrimeIntellect/Qwen3-0.6B-Reverse-Text-SFT"
max_steps = 100
batch_size = 128
rollouts_per_example = 8

env_file = ["secrets.env", "api-keys.env"]  # Loaded relative to config file

[sampling]
max_tokens = 2048

[[env]]
id = "your-username/your-env"


```

### **Full Config with Advanced Options**

```toml
name = "my-training-run"
model = "PrimeIntellect/Qwen3-0.6B-Reverse-Text-SFT"
max_steps = 500
batch_size = 128
rollouts_per_example = 8

# Advanced training options
trajectory_strategy = "interleaved"  # or "branching"
learning_rate = 1e-6
lora_alpha = 16
oversampling_factor = 2.0
max_async_level = 4

env_file = ["secrets.env"]

[sampling]
max_tokens = 2048
temperature = 0.7

[[env]]
id = "your-username/env-1"
args = { split = "train", max_examples = 1000 }

[[env]]
id = "your-username/env-2"

[wandb]
project = "my-project"
entity = "my-team"
name = "my-run-name"

[eval]
interval = 100
num_examples = -1
rollouts_per_example = 1
eval_base_model = true

[[eval.env]]
id = "your-username/eval-env"
args = { split = "test" }
num_examples = 30
rollouts_per_example = 4

[val]
num_examples = 64
rollouts_per_example = 1
interval = 5

[buffer]
online_difficulty_filtering = true
easy_threshold = 0.8
hard_threshold = 0.2
easy_fraction = 0.0
hard_fraction = 0.0


```

## **Configuration Reference**

### **Top-Level Fields**

**Field**

**Type**

**Required**

**Description**

`name`

string

No

Display name for the run

`model`

string

Yes

HuggingFace model name

`max_steps`

int

No

Number of training steps (default = 100)

`batch_size`

int

No

Training batch size (default = 128)

`rollouts_per_example`

int

No

Rollouts per training example (default = 8)

`trajectory_strategy`

string

No

Trajectory strategy: `"interleaved"` or `"branching"`

`learning_rate`

float

No

Learning rate

`lora_alpha`

int

No

LoRA alpha parameter

`oversampling_factor`

float

No

Amount of concurrent rollouts to generate vs. `batch_size`. Recommended value = 2.0 if using online difficulty filtering

`max_async_level`

int

No

How many async steps. Should be ≥ `oversampling_factor`

`env_file`

list

No

Path(s) to .env file(s) containing secrets (relative to config file)

### **`[sampling]` Section**

**Field**

**Type**

**Default**

**Description**

`max_tokens`

int

-

Max tokens to generate

`temperature`

float

-

Sampling temperature (>= 0)

### **`[[env]]` Section (Training Environment)**

Per-environment configuration — one `[[env]]` section per training environment.

**Field**

**Type**

**Required**

**Description**

`id`

string

Yes

Environment ID (owner/name format)

`name`

string

No

Display name (useful when using multiple copies of the same environment with different args)

`args`

table

No

Extra args passed to environment's `load_environment()`

### **`[eval]` Section (Optional)**

Configure online evals to run periodically during RL training.

**Field**

**Type**

**Description**

`interval`

int

Run eval every N steps

`num_examples`

int

Default number of examples for all eval environments (-1 = all)

`rollouts_per_example`

int

Default rollouts per example for all eval environments

`eval_base_model`

bool

Whether to also evaluate the base model

### **`[[eval.env]]` Section (Eval Environments)**

Per-environment eval configuration — one `[[eval.env]]` section per eval.

**Field**

**Type**

**Required**

**Description**

`id`

string

Yes

Environment ID (owner/name format)

`name`

string

No

Display name

`args`

table

No

Custom `load_environment()` args

`num_examples`

int

No

Number of examples to evaluate (overrides `[eval]` default)

`rollouts_per_example`

int

No

Rollouts per eval example (overrides `[eval]` default)

### **`[val]` Section (Optional)**

Configure validation during training.

**Field**

**Type**

**Description**

`num_examples`

int

Number of validation examples

`rollouts_per_example`

int

Rollouts per validation example

`interval`

int

Run validation every N steps

### **`[buffer]` Section (Optional)**

Configure buffer for difficulty filtering.

**Field**

**Type**

**Description**

`online_difficulty_filtering`

bool

Enable online difficulty filtering

`easy_threshold`

float

Threshold for easy examples (e.g., 0.8)

`hard_threshold`

float

Threshold for hard examples (e.g., 0.2)

`easy_fraction`

float

Fraction of easy examples to include

`hard_fraction`

float

Fraction of hard examples to include

`env_ratios`

list

Ratio weights for multi-env training (e.g., `[0.5, 0.5]`)

`skip_verification`

bool

Skip verification step

`seed`

int

Random seed for reproducibility

### **`[wandb]` Section (Optional)**

Log metrics to Weights & Biases.

**Field**

**Type**

**Description**

`project`

string

W&B project name

`entity`

string

W&B team/entity

`name`

string

Run name in W&B

## **Notes**

-   **seq_len** is NOT user-configurable — it's set at the cluster level
-   **max_tokens** controls generation length and should be less than cluster's seq_len
-   Temperature must be >= 0 (negative values are rejected)
-   Use `prime rl models` to see available models
-   Environment IDs must be in `owner/name` format

## **Commands Reference**
