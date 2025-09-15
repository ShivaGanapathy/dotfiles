hdfsc() {
  local pattern=$1
  local hadoop_conf_dirs
  local selected_conf_dir

  hadoop_conf_dirs=($(find /etc/hadoop/* -type d))

  if [[ -n "$pattern" ]]; then
    local matching_dirs=($(for dir in "${hadoop_conf_dirs[@]}"; do
      if [[ "$dir" == *"$pattern"* ]]; then
        echo "$dir"
      fi
    done))

    if (( ${#matching_dirs[@]} == 0 )); then
      echo "No matching Hadoop configuration directories found for '$pattern'"
      return 1
    elif (( ${#matching_dirs[@]} == 1 )); then
      selected_conf_dir=${matching_dirs[1]}
    else
      selected_conf_dir=$(printf '%s\n' "${matching_dirs[@]}" | fzf --prompt="Select Hadoop Configuration Directory: ")
      if [[ -z "$selected_conf_dir" ]]; then
        echo "No directory selected."
        return 1
      fi
    fi
  else
    selected_conf_dir=$(printf '%s\n' "${hadoop_conf_dirs[@]}" | fzf --prompt="Select Hadoop Configuration Directory: ")
    if [[ -z "$selected_conf_dir" ]]; then
      echo "No directory selected."
      return 1
    fi
  fi

  export HADOOP_CONF_DIR=$selected_conf_dir
  echo "HADOOP_CONF_DIR set to $HADOOP_CONF_DIR"
}

