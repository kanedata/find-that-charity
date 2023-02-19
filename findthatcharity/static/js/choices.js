document.querySelectorAll('.js-choices').forEach((el) => {
    const choices = new Choices(el, {
        placeholder: true,
        shouldSort: false,
        removeItemButton: true,
        classNames: {
            containerOuter: 'choices w-100 f6 mt2',
            containerInner: 'w-100 pa2 ba bw1 b--gray',
            input: 'base-font',
            inputCloned: 'choices__input--cloned bn w-100',
        },
        itemSelectText: '',
    });
});