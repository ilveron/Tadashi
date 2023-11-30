JAR = "I-DLV-sr-v2.0.0.jar"
LOGS = "input_logs"
ENCODINGS = "idlvsr_encodings"
EXTERNAL_DEFINITION = "external_definition"
IDLVSR_OPTS = "--parallelism=10 --export-idlv-input --json-output"  # --reasoning-mode=0 removed for now
DLV2 = "dlv2"
DLV2_PYTHON = "dlv2-python"
DLV2_OPTS = "-n 0 --silent=0"
SERVICE_ATOMS = ["IN\d+SECONDS", "ALWAYS\d+SECONDS", "ALWAYS_\d+_\d+SECONDS", "IN_\d+SECONDS",
                 "AT_LEAST\d+IN\d+SECONDS", "AT_LEAST\d+IN_\d+_\d+SECONDS", "COUNT[A-Z]+?IN_\d+_\d+SECONDS",
                 "COUNT[A-Z]+?IN_\d+_SECONDS", "AT_LEAST\d+IN_\d+SECONDS"]
