import React from "react";

const steps = [
    ["upload", "Select a CSV file"],
    ["adddata", "Add charity details."],
    ["download", "Download data."],
]

export default class ReconcileStage extends React.Component {

    getCurrentStepKey(){
        return steps.findIndex(step => step[0] === this.props.stage)
    }

    getStepState(step_to_check){
        const current_step = this.getCurrentStepKey();
        if (current_step == step_to_check){
            return 'is-active';
        } else if (current_step > step_to_check){
            return 'is-completed is-success';
        } else {
            return '';
        }
    }

    render() {
        return (
            <div className="steps">
                {steps.map((step, i) =>
                    <div className={"step-item " + this.getStepState(i)} key={i}>
                        <div className="step-marker">
                            <span className="icon">
                                <i className="fa fa-check"></i>
                            </span>
                        </div>
                        <div className="step-details">
                            <p className="step-title">Step {i+1}</p>
                            <p>{step[1]}</p>
                        </div>
                    </div>
                )}
            </div>
        )
    }
}