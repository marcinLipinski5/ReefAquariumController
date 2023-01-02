class Temperature {
  constructor(root) {
    root.innerHTML = Temperature.getHTML();
    
    this.alarm;
    this.temperature;

    this.temperatureElement = {
      temperature: root.querySelector(".temperature__part--control"),
      alarm: root.querySelector(".alarm__btn--control"),
    };

    this.getTemperatureStatus()
  }

  updateInterfaceTemperature() {
    this.temperatureElement.temperature.textContent = this.temperature.toFixed(1).toString().padStart(2, "0")
  }

  updateInterfaceAlarm() {
    if (this.alarm) {
      this.temperatureElement.alarm.innerHTML = `<span class="material-icons">alarm_on</span>`;
      this.temperatureElement.alarm.classList.add("alarm__btn--active");
      this.temperatureElement.alarm.classList.remove("alarm__btn--inactive");
    }else {
      this.temperatureElement.alarm.innerHTML = `<span class="material-icons">alarm_on</span>`;
      this.temperatureElement.alarm.classList.remove("alarm__btn--active");
      this.temperatureElement.alarm.classList.add("alarm__btn--inactive");
    }

  }

  static getHTML() {
    return `
    <p class="label__text__block">Temperature</p>
    <div class="control__text__block">
      <span class="general__text temperature__part--control">0,000</span>
      <span class="general__text__small">°C</span>
    </div>
    <div class="general__button__block">
			<button type="button" class="general__btn alarm__btn--inactive alarm__btn--control">
				<span class="material-icons">alarm_on</span>
      </button>
    </div>
    <div class="general__button__block">
    <button type="button" class="general__btn settings__btn">
      <a class="material-icons" href="/temperature/plot">query_stats</a>
    </button>
  </div>
    <div class="general__button__block">
      <button type="button" class="general__btn settings__btn">
        <a class="material-icons" href="html/settings/temperature.html">settings</a>
			</button>
    </div>
		`;
  }

  getTemperatureStatus(){
    fetch("/temperature/status")
    .then((response) => {return response.json();})
    .then((json) => { this.setTemperatureStatus(json) });
  }

  setTemperatureStatus(json){
    this.alarm = json.alarm
    this.temperature = json.temperature
    this.updateInterfaceAlarm();
    this.updateInterfaceTemperature();
  }

}

new Temperature(document.querySelector(".temperature"));
