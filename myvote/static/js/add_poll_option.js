var createPollForm = null;
var currentOptions = [];
var addOptionBtn = null;
var form = null;

function initAddButton() {
  createPollForm = document.getElementById('create_poll_form');
  currentOptions = document.querySelectorAll('.optionInput');
  addOptionBtn = document.getElementById('add_poll_option');
}


function OptionInput(idNum) {

  this.idNum = idNum;

  this.getId = function() {return this.idNum;}

  this.inputHtml = function() {

    return '<input type="text" maxlength="100" id="id_option'
            + this.idNum
            + '" name="option' + this.idNum
            + '">'
  }
}

function CreatePollForm(createPollForm, currentOptions) {
  this.form = createPollForm;
  this.currentOptions = Array.from(currentOptions);

  this.addOptionInput = function() {
    this.currentOptions.push(this.createOptionInput(this.currentOptions.length + 1));
    this.form.insertBefore(this.currentOptions[this.currentOptions.length - 1], this.form.lastElementChild)
  }

  this.createOptionInput = function(idNum) {
    let inputEl = document.createElement('input');
    inputEl.type = "text";
    inputEl.classList.add("optionInput");
    inputEl.name = "option" + idNum;
    inputEl.id = "id_option" + idNum;
    inputEl.maxLength = 100;
    return inputEl;
  }
}

document.addEventListener('DOMContentLoaded', function() {
  initAddButton();
  form = new CreatePollForm(createPollForm, currentOptions);
  console.log(form);
});
