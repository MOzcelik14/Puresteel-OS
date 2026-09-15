starship init fish | source

alias güncelle="sudo apt update && sudo apt full-upgrade"
alias yükle="sudo apt install"
alias kaldır="sudo apt remove"
alias temizle="sudo apt autoremove --purge && sudo apt clean"
alias ll="ls -lah"
alias cls="clear"

if status is-interactive
    fastfetch
end
