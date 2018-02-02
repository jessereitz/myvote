var createPollForm = null;
var currentOptions = [];
var addOptionBtn = null;


function initAddButton() {
  createPollForm = document.getElementById('create_poll_form');
  currentOptions = document.querySelectorAll('.optionInput');
  addOptionBtn = document.getElementById('add_poll_option');

}

function CreatePollForm(createPollForm, currentOptions) {
  this.form = createPollForm;
  this.currentOptions = Array.from(currentOptions);

  this.addOptionInput = function() {
    if (this.currentOptions.length >= 5) {
      return null;
    }
    this.currentOptions.push(this.createOptionInput(this.currentOptions.length + 1));
    this.form.insertBefore(this.currentOptions[this.currentOptions.length - 1].label, this.form.lastElementChild);
    this.form.insertBefore(this.currentOptions[this.currentOptions.length - 1], this.form.lastElementChild);
  }

  this.createOptionInput = function(idNum) {
    let inputLabel = document.createElement('label');
    inputLabel.htmlFor = "id_option" + idNum;
    inputLabel.textContent = "option " + idNum + ":";

    let inputEl = document.createElement('input');
    inputEl.type = "text";
    inputEl.classList.add("optionInput");
    inputEl.name = "option" + idNum;
    inputEl.id = "id_option" + idNum;
    inputEl.maxLength = 100;
    inputEl.label = inputLabel;

    return inputEl;
  }
}

document.addEventListener('DOMContentLoaded', function() {
  initAddButton();
  let form = new CreatePollForm(createPollForm, currentOptions);
  document.getElementById('add_poll_option').addEventListener('click', ()=> {form.addOptionInput();});
});
