alias cd='z'
alias sour='source ~/.zshrc'
alias zshc='vim ~/.zshrc'
alias context="python3 ~/Desktop/Code/scripts/context.py "





aliases() {
  fd . ~/.zsh/aliases -t f -0 \
  | fzf --read0 -m --select-1 --exit-0 --print0 \
  | xargs -o -r vim
}


