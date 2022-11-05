class Feeding {
  constructor(root) {
    root.innerHTML = Feeding.getHTML();
    
    this.timeTotal;
    this.remainingSeconds;
    this.getFeedingTime();
    this.interval = null;


    this.el = {
      minutes: root.querySelector(".timer__part--minutes"),
      seconds: root.querySelector(".timer__part--seconds"),
      control: root.querySelector(".timer__btn--control"),
    };

    // 
    
    
    this.el.control.addEventListener("click", () => {
      if (this.interval === null) {
        this.start();
      } else {
        this.stop();
      }
    });
  }

  updateInterfaceTime() {
    const minutes = Math.floor(this.remainingSeconds / 60);
    const seconds = this.remainingSeconds % 60;

    this.el.minutes.textContent = minutes.toString().padStart(2, "0");
    this.el.seconds.textContent = seconds.toString().padStart(2, "0");
  }

  updateInterfaceControls() {
    if (this.interval === null) {
      this.sendActivateAction(false)
      this.el.control.innerHTML = `<span class="material-icons">play_arrow</span>`;
      this.el.control.classList.add("timer__btn--start");
      this.el.control.classList.remove("timer__btn--stop");

    } else {
      this.sendActivateAction(true)
      this.el.control.innerHTML = `<span class="material-icons">cancel</span>`;
      this.el.control.classList.add("timer__btn--stop");
      this.el.control.classList.remove("timer__btn--start");
    }
  }

  start() {
    if (this.remainingSeconds === 0) return;
    this.interval = setInterval(() => {
      this.remainingSeconds--;
      this.updateInterfaceTime();
      if (this.remainingSeconds === 0) {
        this.stop();
      }
    }, 1000);
    this.updateInterfaceControls();
  }

  stop() {
    clearInterval(this.interval);
    this.interval = null;
    this.remainingSeconds = this.timeTotal;
    this.updateInterfaceTime();
    this.updateInterfaceControls();
  }

  static getHTML() {
    return `
      <p class="label__text__block">Feeding</p>
      <div class="control__text__block">
			  <span class="general__text timer__part--minutes">00</span>
			  <span class="general__text">:</span>
			  <span class="general__text timer__part--seconds">00</span>
			</div>
      <div class="general__button__block">
        <button type="button" class="general__btn timer__btn--control timer__btn--start">
				<span class="material-icons">play_arrow</span>
      </button>
      </div>
      <div class="general__button__block">
      <button type="button" class="general__btn settings__btn">
        <a class="material-icons" href="feeding-settings.html">settings</a>
			</button>
      </div>
		`;
  }

  getFeedingTime(){
    fetch("http://127.0.0.1:5000/feeding/feeding-duration")
    .then((response) => {return response.json();})
    .then((json) => { this.setFeedingTime(json) });
  }

  setFeedingTime(json){
    this.remainingSeconds = json.feeding_duration
    this.timeTotal = this.remainingSeconds
    this.updateInterfaceTime();
  }
  
  sendActivateAction(activate) {
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "http://127.0.0.1:5000/feeding/start", true);
    xhttp.setRequestHeader("Content-type", "text/plain");
    xhttp.send(JSON.stringify({"activate": activate}));
  }

}

new Feeding(document.querySelector(".feeding"));
