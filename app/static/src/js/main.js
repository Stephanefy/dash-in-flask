const burger = document.querySelector('.hamburger')
const dropDownMenu = document.querySelector('.menu')


function burgerToggle(){
    burger.classList.toggle('is-active')
    dropDownMenu.classList.toggle('show')
}

burger.addEventListener('click', burgerToggle)