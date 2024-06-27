
function obsidian-open() {
    # Open a file in Obsidian
    target_file=$1
    target_vault=$2

    if [ -z "$target_file" ]; then
        target_file=$(f "*.md" | default-fuzzy-finder)
    fi

    if [ -z "$target_vault" ]; then
        open "obsidian://open?file=${target_file}"
    else
        open "obsidian://open?vault=${target_vault}&file=${target_file}"
    fi
}
alias obo="obsidian-open"


