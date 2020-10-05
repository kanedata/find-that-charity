const tabs = document.querySelectorAll(".tabs");

tabs.forEach(function(tab){

  var tab_selectors = tab.querySelectorAll('a');
  function selectTab(selectedTab){
    tab_selectors.forEach((tab) => {
      if(tab.dataset.tabid == selectedTab){
        tab.dataset.tabactive = "true";
        tab.classList.add("white", "bg-gray");
        tab.classList.remove("near-black");
        document.getElementById(tab.dataset.tabid).style = "display: block";
      } else {
        delete tab.dataset.tabactive;
        tab.classList.add("near-black");
        tab.classList.remove("white", "bg-gray");
        document.getElementById(tab.dataset.tabid).style = "display: none";
      }
    });
  }

  tab_selectors.forEach((el) => {
    el.onclick = function(ev){
      ev.preventDefault();
      selectTab(el.dataset.tabid);
    }
    if(el.dataset.tabactive){
      selectTab(el.dataset.tabid);
    }
  });

});