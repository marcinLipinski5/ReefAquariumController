class AutoRefill {
  constructor(root) {
    root.innerHTML = AutoRefill.getHTML();
    
    this.alarm;
    this.daily_refill_flow;

    this.refill = {
      flow: root.querySelector(".flow__part--control"),
      alarm: root.querySelector(".alarm__btn--control"),
    };

    this.getRefillStatus()
  }

  updateInterfaceFlowCalc() {
    this.refill.flow.textContent = this.daily_refill_flow.toFixed(0).toString()
  }

  updateInterfaceAlarm() {
    if (this.alarm) {
      this.refill.alarm.innerHTML = `<span class="material-icons">alarm_on</span>`;
      this.refill.alarm.classList.add("alarm__btn--active");
      this.refill.alarm.classList.remove("alarm__btn--inactive");
    }else {
      this.refill.alarm.innerHTML = `<span class="material-icons">alarm_on</span>`;
      this.refill.alarm.classList.remove("alarm__btn--active");
      this.refill.alarm.classList.add("alarm__btn--inactive");
    }

  }

  static getHTML() {
    return `
    <p class="label__text__block">Auto refill</p>
    <div class="control__text__block">
      <span class="general__text flow__part--control">0,000</span>
      <span class="general__text__small">ml</span>
    </div>
    <div class="general__button__block">
			<button type="button" class="general__btn alarm__btn--inactive alarm__btn--control">
				<span class="material-icons">alarm_on</span>
      </button>
    </div>
    <div class="general__button__block">
    <button type="button" class="general__btn settings__btn">
      <a class="material-icons" href="/auto_refill/plot">query_stats</a>
    </button>
  </div>
    <div class="general__button__block">
      <button type="button" class="general__btn settings__btn">
        <a class="material-icons" href="html/settings/auto_refill.html">settings</a>
			</button>
    </div>
		`;
  }

  getRefillStatus(){
    fetch("/auto_refill/status")
    .then((response) => {return response.json();})
    .then((json) => { this.setRefillStatus(json) });
  }

  setRefillStatus(json){
    this.alarm = json.alarm
    this.daily_refill_flow = json.daily_refill_flow
    this.updateInterfaceAlarm();
    this.updateInterfaceFlowCalc();
  }

}

new AutoRefill(document.querySelector(".auto-refill"));
