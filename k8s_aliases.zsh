alias k='kubectl'

kctx() {
  local myctx
  myctx=$(kubectl config get-contexts -o name | fzf) || return
  kubectl config use-context "$myctx"
}

kns() {
  local myns
  myns=$(kubectl get ns --no-headers -o custom-columns=:metadata.name | fzf) || return
  kubectl config set-context --current --namespace="$myns" >/dev/null
  printf 'Switched to namespace: %s\n' "$myns"
}

alias ktoken='kubectl imc-rbac get token'
