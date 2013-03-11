HISTFILE=~/.histfile
HISTSIZE=1000
SAVEHIST=1000
setopt inc_append_history
setopt hist_ignore_all_dups

# map Delete, Home, End keys
bindkey "^[[3~" delete-char
bindkey "^[[1~" beginning-of-line
bindkey "^[[4~" end-of-line
bindkey "\eOH" beginning-of-line
bindkey "\eOF" end-of-line

# find previous commands matching current input with up / down
bindkey "^[[A" history-beginning-search-backward
bindkey "^[[B" history-beginning-search-forward

autoload -Uz compinit
compinit

autoload -U promptinit
promptinit
prompt walters


alias ls='ls --color=auto'
alias ll='ls -lF'
alias la='ls -aF'
alias c='clear'
