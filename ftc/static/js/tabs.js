// const tabs = document.querySelectorAll(".tabs");

// tabs.forEach(function(tab){

//   var tab_selectors = tab.querySelectorAll('a');
//   function selectTab(selectedTab){
//     tab_selectors.forEach((tab) => {
//       if(tab.dataset.tabid == selectedTab){
//         tab.dataset.tabactive = "true";
//         tab.classList.add("white", "bg-gray");
//         tab.classList.remove("near-black");
//         document.getElementById(tab.dataset.tabid).style = "display: block";
//       } else {
//         delete tab.dataset.tabactive;
//         tab.classList.add("near-black");
//         tab.classList.remove("white", "bg-gray");
//         document.getElementById(tab.dataset.tabid).style = "display: none";
//       }
//     });
//   }

//   tab_selectors.forEach((el) => {
//     el.onclick = function(ev){
//       ev.preventDefault();
//       selectTab(el.dataset.tabid);
//     }
//     if(el.dataset.tabactive){
//       selectTab(el.dataset.tabid);
//     }
//   });

// });

const SECTIONS = document.querySelectorAll(".org-panel");
const TAB_BAR = document.querySelector("#org-panel-tabs");


// store the scroll position
var keepScroll = false;

function selectTab(selectedTab){
  SECTIONS.forEach((el) => {
    var tab = TAB_BAR.querySelector('ul a[href="#' + el.id + '"]');
    if(el.id == selectedTab){
      el.dataset.tabactive = "true";
      tab.classList.replace("near-black", "white");
      tab.classList.add("bg-gray");
      el.querySelector(".org-panel-contents").style = "display: block";
    } else {
      delete el.dataset.tabactive;
      tab.classList.replace("white", "near-black");
      tab.classList.remove("bg-gray");
      el.querySelector(".org-panel-contents").style = "display: none";
    }
  });
  
  if (keepScroll !== false) {
    window.scrollTo(window.scrollX, keepScroll);
    keepScroll = false;
  }
}

if(SECTIONS.length>1){
  TAB_BAR.classList.remove("dn");

  SECTIONS.forEach((el) => {
    var section_title = el.querySelector(".org-panel-title");
    section_title.classList.add("dn");
    var li = document.createElement("li");
    li.classList.add(...['mr2']);
    var a = document.createElement("a");
    a.classList.add('link', 'pa2', 'underline-hover', 'white', 'bg-gray');
    a.innerText = section_title.innerText;
    a.href = '#' + el.id;
    // a.dataset.tabid = el.id;
    a.onclick = (ev) => {
      if (window.location.hash === ev.target.href) {
        ev.preventDefault(); 
      } else {
        keepScroll = window.scrollY;
      }
    }
    li.append(a);
    TAB_BAR.querySelector("ul").appendChild(li);
  });

  window.addEventListener('hashchange', (ev) => {
    selectTab(location.hash.slice(1));
  });

  if(location.hash){
    selectTab(location.hash.slice(1));
  } else {
    selectTab(SECTIONS[0].id);
  }
}