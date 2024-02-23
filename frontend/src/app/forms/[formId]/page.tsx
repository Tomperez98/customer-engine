'use client'
import Layout from '@/components/layout'
import useGetForms from '@/hooks/useGetForms'
import React from 'react'

const FormDetail = ({params}: {params: {formId: string}}) => {
    const {formId} = params
    const {data, isLoading} = useGetForms(formId)
    return (
        <Layout>
            <div className='flex flex-col'>
                <p>{data.form_id}</p>
                <p>{data.name}</p>
            </div>
        </Layout>
    )
}

export default FormDetail
