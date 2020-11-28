import graphene
from graphene_django import DjangoObjectType
from .models import Prank

class PrankType(DjangoObjectType):
    class Meta:
        model = Prank


class Query(graphene.ObjectType):
    pranks = graphene.List(PrankType)

    def resolve_pranks(self, info):
        return Prank.objects.all()


class CreatePrank(graphene.Mutation):
    prank = graphene.Field(PrankType)


    class Arguments:
        title = graphene.String()
        description = graphene.String()
        url = graphene.String()
    
    def mutate(self, info, title, description, url):
        user = info.context.user or None

        if user.is_anonymous:
            raise Exception('Log in to add a prank.')

        prank = Prank(title=title, description=description, url=url, posted_by=user)
        prank.save()
        return CreatePrank(prank=prank)


class UpdatePrank(graphene.Mutation):
    prank = graphene.Field(PrankType)

    class Arguments:
        prank_id = graphene.Int(required=True)
        title = graphene.String()
        description = graphene.String()
        url = graphene.String()
    
    def mutate(self, info, prank_id, title, url, description):

        user = info.context.user
        prank = Prank.objects.get(id=prank_id)

        if prank.posted_by != user:
            raise Exception('Not permitted to update this track.')

        prank.title = title
        prank.description = description
        prank.url = url
        prank.save()

        return UpdatePrank(prank=prank)


class DeleteTraack(graphene.Mutation):
    prank_id = graphene.Int()

    class Arguments:
        prank_id = graphene.Int(required=True)

    def mutate(self, info, prank_id):
        user = info.context.user
        prank = Prank.objects.get(id=prank_id)

        if prank.posted_by != user:
            raise Exception('Not permitted to delete this track.')

        prank.delete()

        return DeletePrank(prank_id=prank_id)


class Mutation(graphene.ObjectType):
    create_prank = CreatePrank.Field()
    update_prank = UpdatePrank.Field()