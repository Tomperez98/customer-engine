'use client'

import Layout from '@/components/layout'
import {FORM_TEMPLATE} from '@/constants/formFields'
import useCreateForm from '@/hooks/forms/useCreateForm'
import {useCallback, useEffect, useState} from 'react'
import {FormTemplate} from '@/types/Forms'
import {redirect} from 'next/navigation'
import FormCreationForm from '@/components/forms/FormCreationForm'

const CreateForm = () => {
    const [formTemplate, setFormTemplate] =
        useState<FormTemplate>(FORM_TEMPLATE)
    const [shouldRedirect, setShouldRedirect] = useState<boolean>(false)
    const {submit} = useCreateForm(formTemplate)

    const handleCreateForm = useCallback(async () => {
        await submit()
        setShouldRedirect(true)
    }, [submit])

    useEffect(() => {
        if (shouldRedirect) {
            redirect('/dashboard')
        }
    }, [shouldRedirect])

    return (
        <Layout>
            <section className='flex flex-col'>
                <h1 className='mb-4 text-3xl font-extrabold text-neutral-800'>
                    Crear formulario
                </h1>
                <div className='flex w-full flex-col gap-4 rounded-md bg-white p-8 shadow-md'>
                    <FormCreationForm
                        createAction={handleCreateForm}
                        formTemplate={formTemplate}
                        setFormTemplate={setFormTemplate}
                    />
                </div>
            </section>
        </Layout>
    )
}

export default CreateForm
