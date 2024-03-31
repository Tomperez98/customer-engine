import {FormKeys} from '@/types/Forms'
import {InputField} from '@/types/Inputs'

export const FORM_FIELDS: InputField[] = [
    {
        name: 'name',
        label: FormKeys['name'],
        editable: true,
        component: 'input',
    },
    {
        name: 'response',
        label: FormKeys['response'],
        editable: true,
        component: 'textarea',
    },
]

export const FORM_TEMPLATE = {
    name: '',
    response: '',
}
