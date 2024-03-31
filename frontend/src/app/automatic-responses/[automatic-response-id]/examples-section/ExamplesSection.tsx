'use client'

import CallToAction from '@/components/CallToAction'
import useGetExamples from '@/hooks/examples/useGetExamples'
import {useEffect, useState} from 'react'
import AddExamples from './AddExamples'
import ExamplesTable from './ExamplesTable'

interface ExamplesSectionProps {
    formId: string
}

const ExamplesSection = ({formId}: ExamplesSectionProps) => {
    const {data, isLoading, refetch} = useGetExamples(formId)
    const [shouldRefetch, setShouldRefetch] = useState<boolean>(false)
    const [shouldShowCallToAction, setShouldShowCallToAction] =
        useState<boolean>(false)

    useEffect(() => {
        if (shouldRefetch) {
            refetch()
            setShouldRefetch(false)
        }
    }, [shouldRefetch])

    useEffect(() => {
        if (data?.examples.length === 0) {
            setShouldShowCallToAction(true)
        }
    }, [data])
    return (
        <section className='mt-8 flex flex-col gap-6'>
            <h2 className=' text-3xl font-extrabold text-slate-800'>
                Ejemplos
            </h2>
            <div className='box-border flex w-full flex-col gap-4 rounded-md bg-white p-8 shadow-md'>
                {shouldShowCallToAction ? (
                    <CallToAction
                        actionLabel='Agregar ejemplos'
                        onClick={() => setShouldShowCallToAction(false)}
                        text='El formulario no tiene ejemplos.'
                    />
                ) : (
                    !isLoading && (
                        <AddExamples
                            formId={formId}
                            setShouldRefetch={setShouldRefetch}
                        />
                    )
                )}
            </div>
            {data && data?.examples.length > 0 && (
                <ExamplesTable
                    data={data}
                    formId={formId}
                    setShouldRefetch={setShouldRefetch}
                />
            )}
        </section>
    )
}

export default ExamplesSection
