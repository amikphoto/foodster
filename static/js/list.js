;(function () {
  htmx.on("htmx:afterSwap", (e) => {
    // Response targeting #dialog => show the modal
    if (e.detail.target.id == "search_list_result") {

        // const dropdownElementList = document.querySelectorAll('.dropdown-toggle')
        // const dropdownList = [...dropdownElementList].map(dropdownToggleEl => new bootstrap.Dropdown(dropdownToggleEl))
        // let select = document.querySelector('#search_list')
        //
        // select.focus();

      // const mrDataLists = document.querySelectorAll(".mr-datalist");
      // for (let id = 0; id < mrDataLists.length; id++) {
      //   let mrDataList = mrDataLists[id];
      //   let mrDataListUL = "";
      //   let mrDataListClone = "";
      //
      //   mrDataListClone =
      //     '<li class="mr-nomatch"></li>' +
      //     mrDataList
      //       .cloneNode(true)
      //       .innerHTML.replaceAll("<option", "<li")
      //       .replaceAll("</option>", "</li>") +
      //     '<li class="mr-noresults"></li>' +
      //     '<li class="mr-minchars"></li>';
      //   mrDataListUL = document.createElement("ul");
      //   mrDataListUL.id = mrDataList.id;
      //   mrDataListUL.className = mrDataList.className + " mr-search";
      //   mrDataListUL.innerHTML = mrDataListClone;
      //
      //   mrDataList.replaceWith(mrDataListUL);

        // if (document.querySelector('input[list="' + mrDataList.id + '"]')) {
        //   document.querySelector('input[list="' + mrDataList.id + '"]').outerHTML =
        //     "";
        // }
      // }

      // const mrSearches = document.querySelectorAll(".mr-search");
      // for (let id = 0; id < mrSearches.length; id++) {
      //   mrSearches[id].style.display = "none";
      //   if (
      //     (mrSearches[id].classList.contains("mr-navbottom") &&
      //       !mrSearches[id].nextElementSibling) ||
      //     (mrSearches[id].classList.contains("mr-navbottom") &&
      //       mrSearches[id].nextElementSibling &&
      //       !mrSearches[id].nextElementSibling.classList.contains("mr-searchinput"))
      //   ) {
      //     mrSearches[id].outerHTML =
      //       mrSearches[id].outerHTML +
      //       '<input type="text" class="mr-searchinput" name="mr-searchinput" placeholder="Search here...">';
      //   } else if (
      //     !mrSearches[id].previousElementSibling ||
      //     (mrSearches[id].previousElementSibling &&
      //       !mrSearches[id].previousElementSibling.classList.contains(
      //         "mr-searchinput"
      //       ))
      //   ) {
      //     mrSearches[id].outerHTML =
      //       '<input type="text" class="mr-searchinput" name="mr-searchinput" placeholder="Search here...">' +
      //       mrSearches[id].outerHTML;
      //   }
      // }
      //
      // const mrTabsNavs = document.querySelectorAll(".mr-tabsnav");
      // for (let id = 0; id < mrTabsNavs.length; id++) {
      //   mrTabsNav(mrTabsNavs[id]);
      // }
      //
      // const mrTabsEles = document.querySelectorAll(".mr-tabs");
      // for (let id = 0; id < mrTabsEles.length; id++) {
      //   mrTabs(mrTabsEles[id]);
      // }
      //
      // const mrSwipeContentEles = document.querySelectorAll(".mr-swipecontent"); //Always run before mr-swipe because it will add the class to child elements
      // for (let id = 0; id < mrSwipeContentEles.length; id++) {
      //   mrSwipeContent(mrSwipeContentEles[id]);
      // }
      //
      // const mrSwipeEles = document.querySelectorAll(".mr-swipe");
      // for (let id = 0; id < mrSwipeEles.length; id++) {
      //   mrSwipe(mrSwipeEles[id]);
      // }
      //
      // const mrScrollNavEles = document.querySelectorAll(
      //   ".mr-scrollnav:not(.mr-swipecontent):not(.mr-horizontalscrollcontent),.mr-verticalscrollnav:not(.mr-swipecontent):not(.mr-horizontalscrollcontent),.mr-horizontalscrollnav:not(.mr-swipecontent):not(.mr-horizontalscrollcontent)"
      // );
      // for (let id = 0; id < mrScrollNavEles.length; id++) {
      //   mrScrollNav(mrScrollNavEles[id]);
      // }
      //
      // const mrDragEles = document.querySelectorAll(
      //   "[class*='mr-'][class*='-drag']:not([class*='-dragcontent']):not([class*='-draganddrop']),[class*='-dragcontent'] > *, [class*='mr-'][class*='-swipe']:not([class*='-swipecontent']),[class*='mr-'][class*='-swipecontent'] > *"
      // );
      // for (let id = 0; id < mrDragEles.length; id++) {
      //   const mrDragEle = mrDragEles[id];
      //   mrDragEle.classList.remove("mr-dragging");
      //   let pos = { top: 0, left: 0, x: 0, y: 0 };
      //   const mouseDownHandler = function (e) {
      //     setTimeout(function () {
      //       mrDragEle.classList.add("mr-dragging");
      //     }, 250);
      //     pos = {
      //       left: mrDragEle.scrollLeft,
      //       top: mrDragEle.scrollTop,
      //       x: e.clientX,
      //       y: e.clientY,
      //     };
      //     document.addEventListener("mousemove", mouseMoveHandler);
      //     document.addEventListener("mouseup", mouseUpHandler);
      //   };
      //   const mouseMoveHandler = function (e) {
      //     const dx = e.clientX - pos.x;
      //     const dy = e.clientY - pos.y;
      //     mrDragEle.scrollTop = pos.top - dy;
      //     mrDragEle.scrollLeft = pos.left - dx;
      //   };
      //   const mouseUpHandler = function () {
      //     mrDragEle.classList.remove("mr-dragging");
      //     mrDragEle.style.removeProperty("user-select");
      //     document.removeEventListener("mousemove", mouseMoveHandler);
      //     document.removeEventListener("mouseup", mouseUpHandler);
      //   };
      //   mrDragEle.addEventListener("mousedown", mouseDownHandler);
      // }




    }
  })
})()
