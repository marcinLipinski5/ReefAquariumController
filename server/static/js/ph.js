class Ph {
  constructor(root) {
    root.innerHTML = Ph.getHTML();
    
    this.alarm;
    this.ph;

    this.phElement = {
      ph: root.querySelector(".ph__part--control"),
      alarm: root.querySelector(".alarm__btn--control"),
    };

    this.getPhStatus()
  }

  updateInterfacePh() {
    this.phElement.ph.textContent = this.ph.toFixed(1).toString().padStart(2, "0")
  }

  updateInterfaceAlarm() {
    if (this.alarm) {
      this.phElement.alarm.innerHTML = `<span class="material-icons">alarm_on</span>`;
      this.phElement.alarm.classList.add("alarm__btn--active");
      this.phElement.alarm.classList.remove("alarm__btn--inactive");
    }else {
      this.phElement.alarm.innerHTML = `<span class="material-icons">alarm_on</span>`;
      this.phElement.alarm.classList.remove("alarm__btn--active");
      this.phElement.alarm.classList.add("alarm__btn--inactive");
    }

  }

  static getHTML() {
    return `
    <p class="label__text__block">pH</p>
    <div class="control__text__block">
      <span class="general__text ph__part--control">0,000</span>
    </div>
    <div class="general__button__block">
			<button type="button" class="general__btn alarm__btn--inactive alarm__btn--control">
				<span class="material-icons">alarm_on</span>
      </button>
    </div>
    <div class="general__button__block">
    <button type="button" class="general__btn settings__btn">
      <a class="material-icons" href="/ph/plot">query_stats</a>
    </button>
  </div>
    <div class="general__button__block">
      <button type="button" class="general__btn settings__btn">
        <a class="material-icons" href="html/settings/ph.html">settings</a>
			</button>
    </div>
		`;
  }

  getPhStatus(){
    fetch("/ph/status")
    .then((response) => {return response.json();})
    .then((json) => { this.setPhStatus(json) });
  }

  setPhStatus(json){
    this.alarm = json.alarm
    this.ph = json.ph
    this.updateInterfaceAlarm();
    this.updateInterfacePh();
  }

}

new Ph(document.querySelector(".ph"));
