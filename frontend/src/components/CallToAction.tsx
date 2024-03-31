import Button from './Button'

interface CallToActionProps {
    actionLabel: string
    onClick: () => void
    text: string
}

const CallToAction = ({actionLabel, onClick, text}: CallToActionProps) => {
    return (
        <div className='flex h-full w-full flex-col items-center justify-center gap-2 py-4'>
            <p>{text}</p>
            <Button onClick={onClick} label={actionLabel} />
        </div>
    )
}

export default CallToAction
