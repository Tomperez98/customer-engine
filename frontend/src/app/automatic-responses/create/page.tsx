'use client'

import Layout from '@/components/layout'
import {FORM_TEMPLATE} from '@/constants/formFields'
import {useState} from 'react'

const CreateForm = () => {
    const [formTemplate, setFormTemplate] = useState(FORM_TEMPLATE)
    return (
        <Layout>
            <section className='flex flex-col'>
                <h1 className='mb-4 text-3xl font-extrabold text-slate-800'>
                    Crear formulario
                </h1>
                <div className='w-full rounded-md bg-white p-8 shadow-md'>
                    <div className='flex flex-col'>
                        <label htmlFor='name'>nombre</label>
                        <input name='name' type='text' />
                    </div>
                    <div>
                        <label htmlFor='name'>nombre</label>
                        <input name='name' type='text' />
                    </div>
                    <div className='flex w-full flex-row items-center justify-end gap-2'>
                        <button>Descartar</button>
                        <button
                            className='disabled:text-gray-300'
                            onClick={() => console.log('test')}>
                            Guardar
                        </button>
                    </div>
                </div>
            </section>
        </Layout>
    )
}

export default CreateForm
