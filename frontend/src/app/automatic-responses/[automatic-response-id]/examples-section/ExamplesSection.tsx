'use client'

import CallToAction from '@/components/CallToAction'
import useGetExamples from '@/hooks/examples/useGetExamples'
import {useEffect, useState} from 'react'
import AddExamples from './AddExamples'
import ExamplesTable from './ExamplesTable'
import IconButton from '@/components/IconButton'
import {MdAddCircle} from 'react-icons/md'
import {cyan400} from '@/constants/colors'
import {ClipLoader} from 'react-spinners'

interface ExamplesSectionProps {
    formId: string
}

const ExamplesSection = ({formId}: ExamplesSectionProps) => {
    const [isAddExamplesModalOpen, setIsAddExamplesModalOpen] =
        useState<boolean>(false)
    const {data, isLoading, refetch} = useGetExamples(formId)
    const [shouldRefetch, setShouldRefetch] = useState<boolean>(false)

    useEffect(() => {
        if (shouldRefetch) {
            refetch()
            setShouldRefetch(false)
        }
    }, [shouldRefetch])

    return (
        <>
            <AddExamples
                isOpen={isAddExamplesModalOpen}
                setIsOpen={setIsAddExamplesModalOpen}
                formId={formId}
                setShouldRefetch={setShouldRefetch}
            />
            <section className='mt-8 flex flex-col gap-6'>
                <div className='flex items-center gap-2'>
                    <h2 className='pb-1 text-3xl font-extrabold text-slate-800'>
                        Ejemplos
                    </h2>
                    <IconButton
                        size='text-xl'
                        tooltip='Agregar ejemplos'
                        onClick={() => setIsAddExamplesModalOpen(true)}
                        Icon={MdAddCircle}
                    />
                    {isLoading && <ClipLoader color={cyan400} size={18} />}
                </div>

                {data?.examples.length === 0 ? (
                    <div className='box-border flex w-full flex-col gap-4 rounded-md bg-white p-8 shadow-md'>
                        <CallToAction
                            actionLabel='Agregar ejemplos'
                            onClick={() => setIsAddExamplesModalOpen(true)}
                            text='El formulario no tiene ejemplos.'
                        />
                    </div>
                ) : (
                    data && (
                        <ExamplesTable
                            data={data}
                            formId={formId}
                            setShouldRefetch={setShouldRefetch}
                        />
                    )
                )}
            </section>
        </>
    )
}

export default ExamplesSection
