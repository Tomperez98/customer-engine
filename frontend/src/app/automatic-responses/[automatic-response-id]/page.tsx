'use client'
import Layout from '@/components/layout'
import FormDetailsSection from './FormDetailsSection'
import ExamplesSection from './examples-section/ExamplesSection'

const FormDetail = ({params}: {params: {'automatic-response-id': string}}) => {
    const {'automatic-response-id': formId} = params

    return (
        <Layout>
            <FormDetailsSection formId={formId} />
            <ExamplesSection formId={formId} />
        </Layout>
    )
}

export default FormDetail
