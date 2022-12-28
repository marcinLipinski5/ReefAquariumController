class Fan {
  constructor(root) {
    root.innerHTML = Fan.getHTML();
    
    this.level;
    this.dutyCycle;

    this.fanElement = {
      duty_cycle: root.querySelector(".duty_cycle__part--control"),
      level: root.querySelector(".level__btn--control"),
    };

    this.getFanStatus()
  }

  updateInterfaceDutyCycle() {
    this.fanElement.duty_cycle.textContent = this.dutyCycle.toString().padStart(2, "0")
  }

  updateInterfaceLevel() {
    if (this.level == 'freeze') {
      this.fanElement.level.innerHTML = `<span class="material-symbols-outlined">mode_fan</span>`;
      this.fanElement.level.classList.remove("alarm__btn--active");
      this.fanElement.level.classList.remove("alarm__btn--inactive");
      this.fanElement.level.classList.add("alarm__btn--freeze");
    }else if (this.level == 'normal'){
      this.fanElement.level.innerHTML = `<span class="material-symbols-outlined">mode_fan</span>`;
      this.fanElement.level.classList.remove("alarm__btn--active");
      this.fanElement.level.classList.add("alarm__btn--inactive");
      this.fanElement.level.classList.remove("alarm__btn--freeze");
    }else {
      this.fanElement.level.innerHTML = `<span class="material-symbols-outlined">mode_fan</span>`;
      this.fanElement.level.classList.add("alarm__btn--active");
      this.fanElement.level.classList.remove("alarm__btn--inactive");
      this.fanElement.level.classList.remove("alarm__btn--freeze");
    }
  }

  static getHTML() {
    return `
    <p class="label__text__block">Fan PWM</p>
    <div class="control__text__block">
      <span class="general__text duty_cycle__part--control">0,000</span>
      <span class="general__text__small">%</span>
    </div>
    <div class="general__button__block">
			<button type="button" class="general__btn alarm__btn--inactive level__btn--control">
      <span class="material-symbols-outlined">mode_fan</span>
      </button>
    </div>
    <div class="general__button__block">
    <button type="button" class="general__btn settings__btn__inactive">
      <a class="material-icons">query_stats</a>
    </button>
  </div>
    <div class="general__button__block">
      <button type="button" class="general__btn settings__btn">
        <a class="material-icons" href="html/settings/fan.html">settings</a>
			</button>
    </div>
		`;
  }

  getFanStatus(){
    fetch("/fan/status")
    .then((response) => {return response.json();})
    .then((json) => { this.setFanStatus(json) });
  }

  setFanStatus(json){
    this.level = json.level
    this.dutyCycle = json.duty_cycle
    this.updateInterfaceDutyCycle();
    this.updateInterfaceLevel();
  }

}

new Fan(document.querySelector(".fan"));
