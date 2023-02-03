function setupCopyText() {
    document.querySelectorAll(".copy-text").forEach((el) => {
        if (el.dataset.target) {
            el.onclick = (ev) => {
                ev.preventDefault();
                console.log(el.dataset.target);
                navigator.clipboard.writeText(el.dataset.target).then(() => {
                    const toast = document.createElement("span");
                    toast.classList = ['ml2 pa1 bg-dark-gray white f7 br2 absolute']
                    toast.innerText = "Copied!";
                    ev.target.after(toast);
                    setTimeout(() => {
                        toast.parentNode.removeChild(toast);
                    }, 2000);
                });
            };
        }
    });
}
setupCopyText();