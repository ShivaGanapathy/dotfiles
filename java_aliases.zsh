jv() {
  local version=$1
  local java_dirs
  local selected_java

  # Get the list of installed Java versions
  java_dirs=($(ls -d /Library/Java/JavaVirtualMachines/*))

  local matching_java_dirs=($(for dir in "${java_dirs[@]}"; do
    if [[ "$dir" == *"$version"* ]]; then
      echo "$dir"
    fi
  done))

  if (( ${#matching_java_dirs[@]} == 0 )); then
    echo "No matching Java versions found for '$version'"
    return 1
  elif (( ${#matching_java_dirs[@]} == 1 )); then
    selected_java=${matching_java_dirs[1]}
  else
    selected_java=$(printf '%s\n' "${matching_java_dirs[@]}" | fzf --prompt="Select Java version: ")
    if [[ -z "$selected_java" ]]; then
      echo "No Java version selected."
      return 1
    fi
  fi

  export JAVA_HOME="$selected_java/Contents/Home"
  echo "JAVA_HOME set to $JAVA_HOME"
}

alias mci='mvn clean install -DskipTests=true -T1C -Daether.dependencyCollector.impl=bf -Dmaven.artifact.threads=500'
alias spo='mvn spotless:apply'
