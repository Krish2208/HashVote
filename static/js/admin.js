function edit(id, name, email, branch){
    document.getElementById("edit_name").value = name;
    document.getElementById("edit_email").value = email;
    document.getElementById("edit_branch").value = branch;
    document.getElementById("edit_voter").action = "/edit/voter/" + id;
}