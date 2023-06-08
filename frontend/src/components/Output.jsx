import { useRef, useEffect } from "react";

var katex = require('katex');

function Latex({content}) {
    const container = useRef();

    useEffect(() => {
        katex.render(content, container.current);
    }, [content]);

    return <div ref={container} />
}

function Section({latex, name, content}) {
    return (
        <div className="flex flex-col gap-4">
            <h1 className="my-h1">{name}</h1>
            <div className="font-mono p-4 rounded-md bg-rose-800 text-rose-300">
                {content.map(x => latex ? <Latex content={x}></Latex> : content)}
            </div>
        </div>
    )
}

export default function Output({response}) {
    if (response) {
        if (!response.ok) {
            return (
                <div className="mt-10">
                    <Section name="Error" content={[response.content.error]}></Section>
                </div>
            )
        }
        const domain = `\\text{Domain}\\in${response.content.domain}`
        const range = `\\text{Range}\\in${response.content.range}`

        const equation = response.content.equation;
        let simplified = response.content.simplified_equation;
        simplified = equation == simplified
            ? [equation]
            : ['\\text{false}', '\\text{true}'].includes(equation.toLowerCase()) 
            ? [simplified, equation]
            : [equation, simplified];
        
        return (
            <div className="flex flex-col gap-4 mt-10">
                <Section latex={true} name="" content={[domain, range]}></Section>
                <Section latex={true} name="Simplified" content={simplified}></Section>
                <Section latex={true} name="Solution" content={[response.content.latex_solution]}></Section>
                <Section latex={true} name="Derivative" content={[response.content.derivative]}></Section>
            </div>
        )
    } else {
        return (
            <p className="text-rose-300 text-2xl mt-10 bold">Enter some math first...</p>
        )
    }
}