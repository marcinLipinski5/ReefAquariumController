class Alert {
  constructor(root) {
    root.innerHTML = Alert.getHTML();
    

    this.alertElement = {
      alert_window: root.querySelector(".alert_windows__part--control"),
    };

    this.getAlert()
  }

  updateInterface(date, description, action_endpoint, button_text, type) {
    console.log(description)
    this.alertElement.alert_window.innerHTML += 
      `<div class="general__block"
        <p class="label__text__block">Alert</p>
        <p class="alert__text control__text__block">
        [` + date + `] ` + description 
      + `<div class="general__button__block">
          <button type="button" class="alert__button">
          <a href="` + action_endpoint + `?type=` + type +`">` + button_text +`</a>
			    </button>
        </div>`
      +'</p>'
      +'</div>'
  }

  static getHTML() {
    return `
      <span class="general__text__settings alert_windows__part--control"></span>
		`;
  }

  getAlert(){
    fetch("/alert/status")
    .then((response) => {return response.json();})
    .then((json) => { this.setAlert(json) });
  }

  setAlert(json){
    for (var key in json) {
      console.log(json[key])
      var object = json[key]
      this.updateInterface(object.date,
        object.description,
        object.action_endpoint,
        object.button_text,
        object.type)
    }
  }

}

new Alert(document.querySelector(".alert"));
