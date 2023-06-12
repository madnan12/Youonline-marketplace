
function validation(){
var first_name= document.getElementById('first_name').value;
var last_name= document.getElementById('last_name').value;
var gender= document.getElementById('gender').value;
console.log(first_name)
console.log('file running')

if (first_name==""){
    alert("error");
    document.getElementById('first_name2').innerHTML= "* First Name cannot be blank ";
    return false
}
if (last_name==""){
    document.getElementById('last_name2').innerHTML= "* Last Name cannot be blank";
    return false
}
if (gender==""){
    document.getElementById('gender2').innerHTML= "* Gender cannot be blank";
    return false
}

}