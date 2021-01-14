document.querySelectorAll('.js-choices').forEach((el) => {
    const choices = new Choices(el, {
        classNames: {
            containerOuter: 'choices w-100 f6',
            containerInner: 'choices__inner w-100 pa2 ba bw1 b--gray',
            inputCloned: 'choices__input choices__input--cloned bn base-font w-100',
        }
    });
});