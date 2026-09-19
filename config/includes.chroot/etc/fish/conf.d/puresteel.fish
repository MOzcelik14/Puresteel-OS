if status is-interactive
    abbr -a psctl puresteelctl
    function puresteel-help --description 'Show Puresteel command center help'
        puresteelctl --help
    end
end
