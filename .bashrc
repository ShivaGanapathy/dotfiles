copyfile () {
        base64 < "$1" | tr -d '\n' | awk '{print "\033]52;c;" $0 "\a"}'
}
