class General {
  constructor(root) {
    root.innerHTML = General.getHTML();
  }

  static getHTML() {
    return `

    <p class="label__text__block">General</p>
    <div class="general__button__block">
      <button type="button" class="general__btn settings__btn settings__btn__inactive">
        <a class="material-icons">hourglass_disabled</a>
	   </button>
    </div>
    <div class="general__button__block">
      <button type="button" class="general__btn settings__btn">
        <a class="material-icons" href="log/">info</a>
	   </button>
    </div>
    <div class="general__button__block">
      <button type="button" class="general__btn settings__btn">
        <a class="material-icons" href='water_quality/'>science</a>
	   </button>
    </div>
    <div class="general__button__block">
      <button type="button" class="general__btn settings__btn">
        <a class="material-icons" href="notes/">format_list_bulleted_add</a>
	   </button>
    </div>
		`;
  }

}

new General(document.querySelector(".general"));
